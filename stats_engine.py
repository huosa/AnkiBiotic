"""
AnkiBiotic - Real-time statistics calculator
Retention, Pace (cards/sec), Time, Studied, and Streak metrics.
"""

from typing import Dict, Any, Tuple
from datetime import datetime, date, timedelta
from aqt import mw

def get_stats_data(lang: str = "ar") -> Dict[str, Any]:
    """
    Computes real-time review stats from revlog:
    - studied_today
    - time_today_seconds
    - time_today_formatted
    - pace (cards/sec or sec/card)
    - retention (percentage of successful reviews today)
    - streak (consecutive days of reviews)
    - counts: new, learn, review
    """
    if not mw or not mw.col:
        time_zero = "0 min" if lang == "en" else "0 دقيقة"
        return {
            "studied": 0,
            "time_formatted": time_zero,
            "time_seconds": 0,
            "pace_cards_per_sec": 0.0,
            "pace_sec_per_card": 0.0,
            "retention": "0%",
            "streak": 0,
            "new_count": 0,
            "learn_count": 0,
            "due_count": 0,
        }

    col = mw.col
    day_cutoff = col.sched.day_cutoff
    if callable(day_cutoff):
        day_cutoff = day_cutoff()
    day_cutoff_ms = (int(day_cutoff) - 86400) * 1000

    # 1. Reviews today: Count & Time
    # type IN (0,1,2,3) = learn, review, relearn, cram
    rev_data = col.db.first(
        """
        SELECT 
            count(), 
            sum(time)/1000.0,
            sum(case when ease > 1 then 1 else 0 end)
        FROM revlog 
        WHERE type IN (0,1,2,3) AND id > ?
        """,
        day_cutoff_ms
    ) or (0, 0.0, 0)

    studied_today = rev_data[0] or 0
    time_seconds = float(rev_data[1] or 0.0)
    successful_reviews = rev_data[2] or 0

    # Retention calculation
    if studied_today > 0:
        retention_val = (successful_reviews / studied_today) * 100.0
        retention_str = f"{retention_val:.1f}%"
    else:
        retention_str = "0%"

    # Pace calculation
    if time_seconds > 0 and studied_today > 0:
        cards_per_sec = studied_today / time_seconds
        sec_per_card = time_seconds / studied_today
    else:
        cards_per_sec = 0.0
        sec_per_card = 0.0

    # Time formatted
    minutes = int(time_seconds // 60)
    hours = int(minutes // 60)
    rem_min = minutes % 60
    if hours > 0:
        time_str = f"{hours}h {rem_min}m" if lang == "en" else f"{hours} ساعة {rem_min} د"
    else:
        time_str = f"{minutes} min" if lang == "en" else f"{minutes} دقيقة"


    # 2. Streak calculation (consecutive days with reviews)
    streak = compute_review_streak()

    # 3. Deck summary counts (due, new, learn) across all decks
    try:
        counts = col.db.first(
            """
            SELECT 
                sum(case when queue IN (1, 3) then 1 else 0 end),
                sum(case when queue = 2 and due <= ? then 1 else 0 end),
                sum(case when queue = 0 then 1 else 0 end)
            FROM cards
            """,
            col.sched.today
        ) or (0, 0, 0)
        learn_c = counts[0] or 0
        due_c = counts[1] or 0
        new_c = counts[2] or 0
    except Exception:
        learn_c = due_c = new_c = 0

    return {
        "studied": studied_today,
        "time_formatted": time_str,
        "time_seconds": round(time_seconds, 1),
        "pace_cards_per_sec": round(cards_per_sec, 2),
        "pace_sec_per_card": round(sec_per_card, 1),
        "retention": retention_str,
        "streak": streak,
        "new_count": new_c,
        "learn_count": learn_c,
        "due_count": due_c,
    }

def compute_review_streak() -> int:
    """Calculate the consecutive daily streak of study."""
    if not mw or not mw.col:
        return 0

    try:
        col = mw.col
        try:
            if hasattr(col, "get_config"):
                rollover_hours = col.get_config("rollover", 4)
            else:
                rollover_hours = col.conf.get("rollover", 4)
        except Exception:
            rollover_hours = 4
        if rollover_hours is None:
            rollover_hours = 4
        rollover_sec = int(rollover_hours * 3600)

        rows = col.db.all(
            """
            SELECT DISTINCT
                STRFTIME('%Y-%m-%d', (id / 1000) - ?, 'unixepoch', 'localtime') as study_day
            FROM revlog
            WHERE type IN (0,1,2,3)
            ORDER BY study_day DESC
            LIMIT 365
            """,
            rollover_sec
        )

        if not rows:
            return 0

        study_dates = {r[0] for r in rows if r[0]}
        curr = date.today()
        today_iso = curr.isoformat()
        yesterday_iso = (curr - timedelta(days=1)).isoformat()

        # Streak can continue from today or yesterday
        streak = 0
        if today_iso in study_dates:
            check_date = curr
        elif yesterday_iso in study_dates:
            check_date = curr - timedelta(days=1)
        else:
            return 0

        while check_date.isoformat() in study_dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak
    except Exception as e:
        print(f"[AnkiBiotic] Error computing streak: {e}")
        return 0

def calculate_eta(stats: Dict[str, Any], lang: str = "ar") -> Dict[str, Any]:
    """
    Computes estimated finish time and remaining duration based on remaining due cards
    and current pace (sec/card).
    """
    try:
        from .i18n import get_t
    except (ImportError, ValueError):
        import sys, os
        _d = os.path.dirname(__file__)
        if _d not in sys.path:
            sys.path.insert(0, _d)
        from i18n import get_t

    t = get_t(lang)

    total_due = stats.get("due_count", 0) + stats.get("learn_count", 0) + stats.get("new_count", 0)
    if total_due <= 0:
        return {
            "all_done": True,
            "total_due": 0,
            "remaining_sec": 0,
            "remaining_str": "0 " + t.get("min_unit", "د"),
            "finish_clock": "",
            "display_text": t.get("eta_all_done", "أكملت جميع بطاقات اليوم! 🌟")
        }

    pace_sec = stats.get("pace_sec_per_card", 0.0)
    if not pace_sec or pace_sec <= 0.5:
        pace_sec = 8.0  # sensible default of 8 seconds per card

    remaining_sec = int(total_due * pace_sec)
    rem_min = int(remaining_sec // 60)
    rem_hr = int(rem_min // 60)
    leftover_min = rem_min % 60

    if rem_hr > 0:
        if lang == "ar":
            rem_str = f"{rem_hr} س و {leftover_min} د"
        else:
            rem_str = f"{rem_hr}h {leftover_min}m"
    else:
        if lang == "ar":
            rem_str = f"{rem_min} دقيقة"
        else:
            rem_str = f"{rem_min} min"

    finish_dt = datetime.now() + timedelta(seconds=remaining_sec)
    finish_clock = finish_dt.strftime("%I:%M %p")
    if lang == "ar":
        finish_clock = finish_clock.replace("AM", "صباحاً").replace("PM", "مساءً")

    eta_tmpl = t.get("eta_remaining", "متبقي تقريباً {time}")
    rem_label = eta_tmpl.format(time=rem_str)
    display_text = f"⏰ {finish_clock} ({rem_label})"

    return {
        "all_done": False,
        "total_due": total_due,
        "remaining_sec": remaining_sec,
        "remaining_str": rem_str,
        "finish_clock": finish_clock,
        "display_text": display_text
    }

def compute_badges(stats: Dict[str, Any], total_reviews_ever: int = 0, lang: str = "ar") -> list:
    """
    Computes the status and progress of all badges and achievements.
    Returns a list of dicts with: id, title, desc, icon, unlocked, progress_str.
    """
    try:
        from .i18n import get_t
    except (ImportError, ValueError):
        import sys, os
        _d = os.path.dirname(__file__)
        if _d not in sys.path:
            sys.path.insert(0, _d)
        from i18n import get_t

    t = get_t(lang)

    streak = stats.get("streak", 0)
    studied = stats.get("studied", 0)
    time_seconds = stats.get("time_seconds", 0.0)
    pace = stats.get("pace_sec_per_card", 0.0)
    due_remaining = stats.get("due_count", 0) + stats.get("learn_count", 0)

    try:
        ret_val = float(str(stats.get("retention", "0")).replace("%", ""))
    except Exception:
        ret_val = 0.0

    # Read daily goal from config
    try:
        from .config import load_config
        cfg = load_config()
        goal_cards = int(cfg.get("daily_goal_cards", 100))
    except Exception:
        goal_cards = 100

    # Check review times for early bird / night owl
    early_bird_unlocked = False
    night_owl_unlocked = False
    if mw and hasattr(mw, "col") and mw.col:
        try:
            day_cutoff = mw.col.sched.day_cutoff
            if callable(day_cutoff):
                day_cutoff = day_cutoff()
            day_cutoff_ms = (int(day_cutoff) - 86400) * 1000
            hours = mw.col.db.list(
                "SELECT CAST(strftime('%H', (id / 1000), 'unixepoch', 'localtime') AS INTEGER) "
                "FROM revlog WHERE id > ? AND type IN (0,1,2,3)",
                day_cutoff_ms
            )
            if hours:
                early_bird_unlocked = any(h < 8 for h in hours)
                night_owl_unlocked = any(h >= 23 for h in hours)
        except Exception:
            pass

    badges_defs = [
        # --- Streaks ---
        {
            "id": "streak_3",
            "title": t.get("badge_streak_3", "شعلة البداية"),
            "desc": t.get("badge_streak_3_desc", "استمرارية لـ 3 أيام متواصلة"),
            "icon": "🔥",
            "unlocked": streak >= 3,
            "progress_str": f"{min(streak, 3)}/3 {t.get('days', 'أيام')}"
        },
        {
            "id": "streak_7",
            "title": t.get("badge_streak_7", "بطل الأسبوع"),
            "desc": t.get("badge_streak_7_desc", "استمرارية لـ 7 أيام متواصلة"),
            "icon": "⚡",
            "unlocked": streak >= 7,
            "progress_str": f"{min(streak, 7)}/7 {t.get('days', 'أيام')}"
        },
        {
            "id": "streak_30",
            "title": t.get("badge_streak_30", "أسطورة الشهر"),
            "desc": t.get("badge_streak_30_desc", "استمرارية لـ 30 يوماً متواصلاً"),
            "icon": "👑",
            "unlocked": streak >= 30,
            "progress_str": f"{min(streak, 30)}/30 {t.get('days', 'أيام')}"
        },
        {
            "id": "streak_100",
            "title": t.get("badge_streak_100", "المئوية الذهبية"),
            "desc": t.get("badge_streak_100_desc", "استمرارية أسطورية لـ 100 يوم"),
            "icon": "🏆",
            "unlocked": streak >= 100,
            "progress_str": f"{min(streak, 100)}/100 {t.get('days', 'أيام')}"
        },
        {
            "id": "streak_180",
            "title": t.get("badge_streak_180", "نصف عام أسطوري"),
            "desc": t.get("badge_streak_180_desc", "استمرارية لـ 180 يوماً متواصلاً دون انقطاع"),
            "icon": "🌟",
            "unlocked": streak >= 180,
            "progress_str": f"{min(streak, 180)}/180 {t.get('days', 'أيام')}"
        },
        {
            "id": "streak_365",
            "title": t.get("badge_streak_365", "الماسة السنوية"),
            "desc": t.get("badge_streak_365_desc", "إكمال عام كامل (365 يوماً) من المذاكرة اليومية"),
            "icon": "💎",
            "unlocked": streak >= 365,
            "progress_str": f"{min(streak, 365)}/365 {t.get('days', 'أيام')}"
        },

        # --- Lifetime Reviews ---
        {
            "id": "century_club",
            "title": t.get("badge_century_club", "نادي الألفية"),
            "desc": t.get("badge_century_club_desc", "تجاوز 1,000 مراجعة إجمالية"),
            "icon": "🎖️",
            "unlocked": total_reviews_ever >= 1000,
            "progress_str": f"{min(total_reviews_ever, 1000)}/1000"
        },
        {
            "id": "century_5k",
            "title": t.get("badge_century_5k", "المحارب المتقدم"),
            "desc": t.get("badge_century_5k_desc", "تجاوز 5,000 مراجعة إجمالية في مسيرتك"),
            "icon": "⚔️",
            "unlocked": total_reviews_ever >= 5000,
            "progress_str": f"{min(total_reviews_ever, 5000)}/5000"
        },
        {
            "id": "century_10k",
            "title": t.get("badge_century_10k", "سيد البطاقات"),
            "desc": t.get("badge_century_10k_desc", "تجاوز 10,000 مراجعة إجمالية"),
            "icon": "👑",
            "unlocked": total_reviews_ever >= 10000,
            "progress_str": f"{min(total_reviews_ever, 10000)}/10000"
        },
        {
            "id": "century_50k",
            "title": t.get("badge_century_50k", "أسطورة الذاكرة"),
            "desc": t.get("badge_century_50k_desc", "تجاوز 50,000 مراجعة إجمالية"),
            "icon": "🌌",
            "unlocked": total_reviews_ever >= 50000,
            "progress_str": f"{min(total_reviews_ever, 50000)}/50000"
        },

        # --- Daily Grind & Stamina ---
        {
            "id": "scholar",
            "title": t.get("badge_scholar", "القارئ الشغوف"),
            "desc": t.get("badge_scholar_desc", "مراجعة 100 بطاقة أو أكثر اليوم"),
            "icon": "📚",
            "unlocked": studied >= 100,
            "progress_str": f"{min(studied, 100)}/100"
        },
        {
            "id": "beast_mode",
            "title": t.get("badge_beast_mode", "الوحش الدراسي"),
            "desc": t.get("badge_beast_mode_desc", "مراجعة 250 بطاقة أو أكثر في يوم واحد"),
            "icon": "🦁",
            "unlocked": studied >= 250,
            "progress_str": f"{min(studied, 250)}/250"
        },
        {
            "id": "marathon",
            "title": t.get("badge_marathon", "الماراثون الفولاذي"),
            "desc": t.get("badge_marathon_desc", "دراسة أكثر من 60 دقيقة فعلية اليوم"),
            "icon": "🌋",
            "unlocked": time_seconds >= 3600,
            "progress_str": f"{int(time_seconds // 60)}/60 {t.get('min_unit', 'د')}"
        },
        {
            "id": "goal_crusher",
            "title": t.get("badge_goal_crusher", "الهدف المحقق"),
            "desc": t.get("badge_goal_crusher_desc", "إنجاز 100% من هدف الدراسة اليومي"),
            "icon": "🎯",
            "unlocked": studied >= goal_cards and goal_cards > 0,
            "progress_str": f"{min(studied, goal_cards)}/{goal_cards}"
        },

        # --- Accuracy & Mastery ---
        {
            "id": "sniper",
            "title": t.get("badge_sniper", "قناص الدقة"),
            "desc": t.get("badge_sniper_desc", "تحقيق نسبة دقة 90% فأعلى اليوم"),
            "icon": "🎯",
            "unlocked": studied >= 10 and ret_val >= 90.0,
            "progress_str": f"{ret_val:.1f}% ({studied} {t.get('reviews', 'مراجعة')})"
        },
        {
            "id": "flawless",
            "title": t.get("badge_flawless", "العلامة الكاملة"),
            "desc": t.get("badge_flawless_desc", "تحقيق نسبة دقة 100% (20 بطاقة فأكثر)"),
            "icon": "💯",
            "unlocked": studied >= 20 and ret_val >= 99.9,
            "progress_str": f"{ret_val:.1f}% ({studied}/20)"
        },
        {
            "id": "clean_slate",
            "title": t.get("badge_clean_slate", "تصفير الرزم"),
            "desc": t.get("badge_clean_slate_desc", "إنهاء جميع البطاقات المستحقة لليوم"),
            "icon": "🧹",
            "unlocked": due_remaining == 0 and studied >= 5,
            "progress_str": ("✅ تم تصفير الرزم" if lang == "ar" else "✅ All clear") if (due_remaining == 0 and studied >= 5) else f"{due_remaining} {t.get('stat_due', 'مستحقة')}"
        },

        # --- Speed & Rhythm ---
        {
            "id": "speed",
            "title": t.get("badge_speed", "السرعة الخارقة"),
            "desc": t.get("badge_speed_desc", "معدل سرعة أقل من 6 ثوانٍ للبطاقة"),
            "icon": "🚀",
            "unlocked": studied >= 10 and 0 < pace <= 6.0,
            "progress_str": f"{pace:.1f} {t.get('stat_pace_unit', 'ث/بطاقة')}"
        },
        {
            "id": "lightning",
            "title": t.get("badge_lightning", "البرق الخاطف"),
            "desc": t.get("badge_lightning_desc", "سرعة أقل من 4 ثوانٍ مع دقة تفوق 85%"),
            "icon": "⚡",
            "unlocked": studied >= 15 and 0 < pace <= 4.0 and ret_val >= 85.0,
            "progress_str": f"{pace:.1f}s • {ret_val:.0f}%"
        },

        # --- Habits & Timings ---
        {
            "id": "early_bird",
            "title": t.get("badge_early_bird", "طائر الصباح"),
            "desc": t.get("badge_early_bird_desc", "إتمام جلسة مراجعة قبل الساعة 8 صباحاً"),
            "icon": "🌅",
            "unlocked": early_bird_unlocked,
            "progress_str": ("✅ محققة اليوم" if lang == "ar" else "✅ Today") if early_bird_unlocked else ("قبل 8:00 ص" if lang == "ar" else "Before 8:00 AM")
        },
        {
            "id": "night_owl",
            "title": t.get("badge_night_owl", "بومة الليل"),
            "desc": t.get("badge_night_owl_desc", "إتمام جلسة مراجعة بعد الساعة 11 مساءً"),
            "icon": "🦉",
            "unlocked": night_owl_unlocked,
            "progress_str": ("✅ محققة اليوم" if lang == "ar" else "✅ Today") if night_owl_unlocked else ("بعد 11:00 م" if lang == "ar" else "After 11:00 PM")
        },

        # --- Antibiotic Med Badges (منظومة المضادات الحيوية السريرية) ---
        {
            "id": "med_penicillin",
            "title": t.get("badge_med_penicillin", "جرعة البنسلين"),
            "desc": t.get("badge_med_penicillin_desc", "إتمام الجرعة الأساسية بمراجعة 30 بطاقة اليوم"),
            "icon": "💊",
            "unlocked": studied >= 30,
            "progress_str": f"{min(studied, 30)}/30"
        },
        {
            "id": "med_azithromycin",
            "title": t.get("badge_med_azithromycin", "أزيثروميسين السريع"),
            "desc": t.get("badge_med_azithromycin_desc", "سرعة فائقة (أقل من 5 ثوانٍ للبطاقة مع 20+ مراجعة)"),
            "icon": "⚡",
            "unlocked": studied >= 20 and 0 < pace <= 5.0,
            "progress_str": f"{pace:.1f}s ({min(studied, 20)}/20)"
        },
        {
            "id": "med_vancomycin",
            "title": t.get("badge_med_vancomycin", "فانكومايسين الخط الأخير"),
            "desc": t.get("badge_med_vancomycin_desc", "جلسة علاج مكثفة (150 بطاقة أو أكثر من 45 دقيقة دراسة)"),
            "icon": "🛡️",
            "unlocked": studied >= 150 or time_seconds >= 2700,
            "progress_str": f"{min(studied, 150)}/150 | {int(time_seconds // 60)}/45 {t.get('min_unit', 'د')}"
        },
        {
            "id": "med_broad_spectrum",
            "title": t.get("badge_med_broad_spectrum", "مضاد واسع الطيف"),
            "desc": t.get("badge_med_broad_spectrum_desc", "تغطية شاملة ومناعة صلبة (دقة 92% فأكثر مع 40+ بطاقة)"),
            "icon": "🧬",
            "unlocked": studied >= 40 and ret_val >= 92.0,
            "progress_str": f"{ret_val:.1f}% ({min(studied, 40)}/40)"
        },
        {
            "id": "med_vaccine",
            "title": t.get("badge_med_vaccine", "لقاح الاستمرارية"),
            "desc": t.get("badge_med_vaccine_desc", "تعزيز المناعة المعرفية بدراسة 5 أيام متتالية دون انقطاع"),
            "icon": "💉",
            "unlocked": streak >= 5,
            "progress_str": f"{min(streak, 5)}/5 {t.get('days', 'أيام')}"
        },
        {
            "id": "med_culture_negative",
            "title": t.get("badge_med_culture_negative", "مزرعة سالبة (تعقيم كامل)"),
            "desc": t.get("badge_med_culture_negative_desc", "القضاء على العدوى بتصفير الرزم بالكامل (15+ بطاقة اليوم)"),
            "icon": "🧪",
            "unlocked": due_remaining == 0 and studied >= 15,
            "progress_str": ("✅ تعقيم كامل" if lang == "ar" else "✅ All clear") if (due_remaining == 0 and studied >= 15) else f"{due_remaining} {t.get('stat_due', 'مستحقة')}"
        },
    ]

    return badges_defs

