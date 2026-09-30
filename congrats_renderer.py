"""
AnkiBiotic - Deck Completed / Victory Screen (شاشة انتهاء الرزمة)
Renders a clinical, rewarding victory dashboard when finishing a deck:
1. Session Snapshot Card (كروت الجلسة، الدقة، الوقت، السرعة)
2. Smart Forecast & Daily Goal (المراجعة القادمة وهدف اليوم)
3. Micro-Celebrations (كونفيتي وتأثيرات احتفالية ناعمة)
4. Memory Consolidation Meter (مؤشر مقاومة منحنى النسيان)
"""

import os
import html
from aqt import mw
from aqt.overview import Overview

from .config import load_config, get_theme_palette, get_font_info
from .stats_engine import get_stats_data
from .i18n import get_t

def render_ankibiotic_congrats(self: Overview) -> None:
    """
    Renders AnkiBiotic's celebratory victory dashboard upon deck completion.
    Replaces Overview._show_finished_screen.
    """
    cfg = load_config()
    lang = cfg.get("language", "ar")
    t = get_t(lang)
    theme_id = cfg.get("theme", "coffee_mocha")
    pal = get_theme_palette(theme_id)

    # Theme colors
    bg = pal.get("bg", "#1a120e")
    card_bg = pal.get("card_bg", "#241a13")
    card_inset = pal.get("card_inset", "#2e2119")
    card_hover = pal.get("card_hover", "#38291e")
    border = pal.get("border", "#4a3729")
    border_subtle = pal.get("border_subtle", "#36271c")
    fg = pal.get("fg", "#faecd0")
    fg_muted = pal.get("fg_muted", "#b89f8c")
    accent = pal.get("accent", "#d4a373")
    accent_hover = pal.get("accent_hover", "#e6be94")
    gold = pal.get("gold", "#f4c06b")

    # Font
    font_id = cfg.get("font_family_preset", "cairo")
    font_info = get_font_info(font_id)
    font_css = font_info.get("family", "'Cairo', sans-serif")
    google_font_url = font_info.get("google_font", "")
    google_font_tag = f'<link rel="stylesheet" href="{google_font_url}">' if google_font_url else ""

    # Current Deck Information
    deck_name = ""
    deck_id = None
    try:
        cur_deck = mw.col.decks.current()
        deck_name = cur_deck.get("name", "")
        deck_id = cur_deck.get("id")
    except Exception:
        pass

    # 1️⃣ Session Snapshot Statistics (إحصاءات الجلسة للرزمة الحالية)
    deck_reviews = 0
    deck_correct = 0
    deck_time_sec = 0.0
    due_tomorrow = 0

    if mw and hasattr(mw, "col") and mw.col and deck_id is not None:
        try:
            dids = mw.col.decks.deck_and_child_ids(deck_id)
            day_cutoff = mw.col.sched.day_cutoff
            if callable(day_cutoff):
                day_cutoff = day_cutoff()
            day_cutoff_ms = (int(day_cutoff) - 86400) * 1000

            # Reviews for this deck today
            row = mw.col.db.first(f"""
                SELECT 
                    count(),
                    sum(case when ease > 1 then 1 else 0 end),
                    sum(time) / 1000
                FROM revlog r
                JOIN cards c ON r.cid = c.id
                WHERE c.did IN ({dids_str}) AND r.id > ? AND r.type IN (0,1,2,3)
            """, day_cutoff_ms)
            if row:
                deck_reviews = row[0] or 0
                deck_correct = row[1] or 0
                deck_time_sec = float(row[2] or 0.0)

            # Cards due tomorrow for this deck
            due_tomorrow = mw.col.db.scalar(f"""
                SELECT count() FROM cards 
                WHERE did IN ({dids_str}) AND queue = 2 AND due = ?
            """, mw.col.sched.today + 1) or 0
        except Exception as e:
            print(f"[AnkiBiotic] Congrats stats query error: {e}")

    # Fallback to daily general stats if session has no specific revlog rows
    all_stats = get_stats_data(lang=lang)
    if deck_reviews == 0:
        deck_reviews = all_stats.get("studied", 0)
        try:
            deck_retention = float(str(all_stats.get("retention", "0")).replace("%", ""))
        except Exception:
            deck_retention = 95.0
        deck_time_sec = all_stats.get("time_seconds", 0.0)
        deck_pace = all_stats.get("pace_sec_per_card", 0.0)
    else:
        deck_retention = (deck_correct / deck_reviews * 100.0) if deck_reviews > 0 else 100.0
        deck_pace = (deck_time_sec / deck_reviews) if deck_reviews > 0 else 0.0

    # Format time
    m = int(deck_time_sec // 60)
    s = int(deck_time_sec % 60)
    if lang == "ar":
        time_formatted = f"{m} د {s} ث" if m > 0 else f"{s} ث"
        pace_formatted = f"{deck_pace:.1f} ث/بطاقة"
    else:
        time_formatted = f"{m}m {s}s" if m > 0 else f"{s}s"
        pace_formatted = f"{deck_pace:.1f} s/card"

    # 3️⃣ Daily Goal Progress (هدف اليوم)
    daily_goal = int(cfg.get("daily_goal_cards", 100))
    total_studied = all_stats.get("studied", 0)
    goal_pct = min(100, int((total_studied / daily_goal) * 100)) if daily_goal > 0 else 100
    goal_remain = max(0, daily_goal - total_studied)
    goal_achieved = total_studied >= daily_goal and daily_goal > 0

    goal_progress_text = t["congrats_goal_progress"].format(
        studied=total_studied, goal=daily_goal, percent=goal_pct
    )
    goal_msg = t["congrats_goal_done"] if goal_achieved else t["congrats_goal_remain"].format(remain=goal_remain)

    # 3️⃣ Next Review Forecast Text
    if due_tomorrow > 0:
        forecast_text = t["congrats_forecast_cards"].format(count=due_tomorrow)
    else:
        forecast_text = t["congrats_forecast_clear"]

    # 7️⃣ Memory Consolidation Meter (مقاومة منحنى النسيان)
    consolidation_boost = min(38, max(14, int(deck_retention * 0.22 + min(deck_reviews, 40) * 0.35)))
    consolidation_pct = min(98, max(70, int(deck_retention * 0.9 + min(deck_reviews, 30) * 0.2)))

    # Clean Anki's original bottom bar
    if hasattr(self, "bottom") and self.bottom:
        try:
            self.bottom.draw("")
        except Exception:
            pass
    if hasattr(mw, "bottomWeb") and mw.bottomWeb:
        try:
            mw.bottomWeb.hide()
        except Exception:
            pass

    full_html = f"""
    <!DOCTYPE html>
    <html lang="{lang}" dir="{t['dir']}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t['congrats_title']}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        {google_font_tag}
        <style>
            :root {{
                --ab-bg: {bg};
                --ab-card-bg: {card_bg};
                --ab-card-inset: {card_inset};
                --ab-card-hover: {card_hover};
                --ab-border: {border};
                --ab-border-subtle: {border_subtle};
                --ab-fg: {fg};
                --ab-fg-muted: {fg_muted};
                --ab-accent: {accent};
                --ab-accent-hover: {accent_hover};
                --ab-gold: {gold};
            }}

            *, *::before, *::after {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                user-select: none;
                -webkit-user-select: none;
            }}

            html, body {{
                width: 100vw;
                height: 100vh;
                margin: 0;
                padding: 0;
                background-color: var(--ab-bg);
                color: var(--ab-fg);
                font-family: {font_css};
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }}

            /* Canvas Confetti Layer */
            #ab-confetti-canvas {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                pointer-events: none;
                z-index: 99;
            }}

            /* Main Victory Container */
            .congrats-wrapper {{
                width: 100%;
                max-width: 680px;
                max-height: 94vh;
                padding: 24px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
                z-index: 10;
                overflow-y: auto;
            }}

            /* Hero Card */
            .congrats-card {{
                width: 100%;
                background: var(--ab-card-bg);
                border: 1px solid var(--ab-border);
                border-radius: 20px;
                padding: 26px 28px;
                box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                animation: popIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
                position: relative;
            }}

            @keyframes popIn {{
                0% {{ opacity: 0; transform: scale(0.92) translateY(16px); }}
                100% {{ opacity: 1; transform: scale(1) translateY(0); }}
            }}

            /* Victory Emblem */
            .victory-emblem-box {{
                width: 74px;
                height: 74px;
                border-radius: 50%;
                background: radial-gradient(circle, var(--ab-card-inset) 0%, var(--ab-card-bg) 100%);
                border: 2px solid var(--ab-gold);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                box-shadow: 0 0 24px rgba(244, 192, 107, 0.35);
                margin-bottom: 12px;
                animation: pulseGlow 2.5s infinite ease-in-out;
            }}

            @keyframes pulseGlow {{
                0%, 100% {{ transform: scale(1); box-shadow: 0 0 20px rgba(244, 192, 107, 0.3); }}
                50% {{ transform: scale(1.06); box-shadow: 0 0 32px rgba(244, 192, 107, 0.55); }}
            }}

            .congrats-header h1 {{
                font-size: 20px;
                font-weight: 800;
                color: var(--ab-fg);
                margin-bottom: 4px;
                letter-spacing: -0.2px;
            }}

            .congrats-header .deck-pill {{
                display: inline-block;
                background: var(--ab-card-inset);
                border: 1px solid var(--ab-border-subtle);
                border-radius: 999px;
                padding: 3px 14px;
                font-size: 12px;
                font-weight: 700;
                color: var(--ab-accent);
                margin-bottom: 6px;
            }}

            .congrats-header p {{
                font-size: 12.5px;
                color: var(--ab-fg-muted);
                line-height: 1.5;
            }}

            /* 1️⃣ 4-Grid Session Snapshot */
            .stats-snapshot-grid {{
                width: 100%;
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
                margin-top: 18px;
            }}

            .snapshot-box {{
                background: var(--ab-card-inset);
                border: 1px solid var(--ab-border);
                border-radius: 12px;
                padding: 10px 8px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 3px;
                transition: transform 0.2s ease, border-color 0.2s ease;
            }}

            .snapshot-box:hover {{
                transform: translateY(-2px);
                border-color: var(--ab-accent);
            }}

            .snapshot-val {{
                font-size: 16px;
                font-weight: 800;
                color: var(--ab-fg);
            }}

            .snapshot-lbl {{
                font-size: 10px;
                font-weight: 700;
                color: var(--ab-fg-muted);
            }}

            /* 7️⃣ Memory Consolidation Meter */
            .memory-meter-box {{
                width: 100%;
                background: var(--ab-card-inset);
                border: 1px solid var(--ab-border);
                border-radius: 14px;
                padding: 12px 16px;
                margin-top: 12px;
                text-align: right;
            }}
            html[dir="ltr"] .memory-meter-box {{
                text-align: left;
            }}

            .memory-meter-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 6px;
            }}

            .memory-meter-title {{
                font-size: 11.5px;
                font-weight: 800;
                color: var(--ab-fg);
            }}

            .memory-meter-boost {{
                font-size: 12px;
                font-weight: 800;
                color: var(--ab-gold);
            }}

            .memory-bar-bg {{
                width: 100%;
                height: 8px;
                background: rgba(0, 0, 0, 0.25);
                border-radius: 999px;
                overflow: hidden;
                position: relative;
            }}

            .memory-bar-fill {{
                height: 100%;
                width: {consolidation_pct}%;
                background: linear-gradient(90deg, var(--ab-accent), var(--ab-gold));
                border-radius: 999px;
                transition: width 1s ease-out;
            }}

            .memory-meter-sub {{
                font-size: 10.5px;
                color: var(--ab-fg-muted);
                margin-top: 6px;
                line-height: 1.4;
            }}

            /* 3️⃣ Daily Goal & Next Forecast Dual Row */
            .forecast-goal-row {{
                width: 100%;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 12px;
            }}

            .info-panel {{
                background: var(--ab-card-inset);
                border: 1px solid var(--ab-border);
                border-radius: 12px;
                padding: 10px 12px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 4px;
                text-align: right;
            }}
            html[dir="ltr"] .info-panel {{
                text-align: left;
            }}

            .info-panel-title {{
                font-size: 10.5px;
                font-weight: 700;
                color: var(--ab-fg-muted);
            }}

            .info-panel-val {{
                font-size: 12px;
                font-weight: 800;
                color: var(--ab-fg);
            }}

            .info-panel-sub {{
                font-size: 10px;
                color: var(--ab-accent);
                font-weight: 600;
            }}

            /* Action Buttons */
            .congrats-actions {{
                display: flex;
                gap: 10px;
                width: 100%;
                margin-top: 18px;
            }}

            .congrats-btn {{
                flex: 1;
                height: 38px;
                border-radius: 10px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                font-size: 12px;
                font-weight: 800;
                cursor: pointer;
                font-family: inherit;
                transition: all 0.2s ease;
                border: none;
            }}

            .btn-primary {{
                background: var(--ab-accent);
                color: #ffffff;
                border: 1px solid var(--ab-accent);
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
            }}
            .btn-primary:hover {{
                background: var(--ab-accent-hover);
                transform: translateY(-1px);
            }}

            .btn-secondary {{
                background: var(--ab-card-inset);
                color: var(--ab-fg);
                border: 1px solid var(--ab-border);
            }}
            .btn-secondary:hover {{
                background: var(--ab-card-hover);
                border-color: var(--ab-accent);
                transform: translateY(-1px);
            }}

            /* Responsive */
            @media (max-width: 580px) {{
                .stats-snapshot-grid {{ grid-template-columns: repeat(2, 1fr); }}
                .forecast-goal-row {{ grid-template-columns: 1fr; }}
                .congrats-actions {{ flex-direction: column; }}
            }}
        </style>
    </head>
    <body>
        <canvas id="ab-confetti-canvas"></canvas>

        <div class="congrats-wrapper">
            <div class="congrats-card">

                <!-- 5️⃣ Micro-Celebration Victory Emblem -->
                <div class="victory-emblem-box">
                    <span>🏆</span>
                </div>

                <div class="congrats-header">
                    <span class="deck-pill">{html.escape(deck_name or t['decks_title'])}</span>
                    <h1>{t['congrats_title']}</h1>
                    <p>{t['congrats_subtitle']}</p>
                </div>

                <!-- 1️⃣ Session Snapshot Card (4-Metrics) -->
                <div class="stats-snapshot-grid">
                    <div class="snapshot-box">
                        <span class="snapshot-val">{deck_reviews}</span>
                        <span class="snapshot-lbl">{t['congrats_stat_studied']}</span>
                    </div>
                    <div class="snapshot-box">
                        <span class="snapshot-val">{deck_retention:.1f}%</span>
                        <span class="snapshot-lbl">{t['congrats_stat_retention']}</span>
                    </div>
                    <div class="snapshot-box">
                        <span class="snapshot-val">{time_formatted}</span>
                        <span class="snapshot-lbl">{t['congrats_stat_time']}</span>
                    </div>
                    <div class="snapshot-box">
                        <span class="snapshot-val">{pace_formatted}</span>
                        <span class="snapshot-lbl">{t['congrats_stat_pace']}</span>
                    </div>
                </div>

                <!-- 7️⃣ Memory Consolidation Meter (مقاومة منحنى النسيان) -->
                <div class="memory-meter-box">
                    <div class="memory-meter-header">
                        <span class="memory-meter-title">🧠 {t['congrats_memory_title']}</span>
                        <span class="memory-meter-boost">+{consolidation_boost}% {t['congrats_stat_retention']}</span>
                    </div>
                    <div class="memory-bar-bg">
                        <div class="memory-bar-fill"></div>
                    </div>
                    <p class="memory-meter-sub">{t['congrats_memory_desc']}</p>
                </div>

                <!-- 3️⃣ Smart Forecast & Daily Goal Status (هدف اليوم والموعد القادم) -->
                <div class="forecast-goal-row">
                    <!-- Daily Goal -->
                    <div class="info-panel">
                        <span class="info-panel-title">🎯 {t['congrats_goal_title']}</span>
                        <span class="info-panel-val">{goal_progress_text}</span>
                        <span class="info-panel-sub">{goal_msg}</span>
                    </div>
                    <!-- Next Forecast -->
                    <div class="info-panel">
                        <span class="info-panel-title">📅 {t['congrats_forecast_title']}</span>
                        <span class="info-panel-val">{forecast_text}</span>
                        <span class="info-panel-sub">✨ {deck_name}</span>
                    </div>
                </div>

                <!-- Action Controls -->
                <div class="congrats-actions">
                    <button class="congrats-btn btn-primary" onclick="pycmd('decks')">
                        <span>{t['congrats_btn_dashboard']}</span>
                    </button>
                    <button class="congrats-btn btn-secondary" onclick="pycmd('studymore')">
                        <span>{t['congrats_btn_custom_study']}</span>
                    </button>
                    <button class="congrats-btn btn-secondary" onclick="pycmd('opts')">
                        <span>{t['congrats_btn_options']}</span>
                    </button>
                </div>

            </div>
        </div>

        <!-- 5️⃣ Confetti Animation Script -->
        <script>
        (function() {{
            var canvas = document.getElementById('ab-confetti-canvas');
            if (!canvas) return;
            var ctx = canvas.getContext('2d');
            var W = window.innerWidth;
            var H = window.innerHeight;
            canvas.width = W;
            canvas.height = H;

            var confettiCount = 55;
            var particles = [];
            var colors = ['{gold}', '{accent}', '#10b981', '#0f82b8', '#ff4d6d', '#ffffff'];

            for (var i = 0; i < confettiCount; i++) {{
                particles.push({{
                    x: Math.random() * W,
                    y: Math.random() * -H * 0.6,
                    r: Math.random() * 5 + 3,
                    d: Math.random() * confettiCount,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    tilt: Math.floor(Math.random() * 10) - 10,
                    tiltAngleIncremental: (Math.random() * 0.07) + 0.05,
                    tiltAngle: 0
                }});
            }}

            var animationFrameId;
            var startTime = Date.now();

            function draw() {{
                ctx.clearRect(0, 0, W, H);
                var elapsed = Date.now() - startTime;
                var alpha = 1.0;
                if (elapsed > 2000) {{
                    alpha = Math.max(0, 1.0 - (elapsed - 2000) / 1000);
                }}

                ctx.globalAlpha = alpha;
                for (var i = 0; i < confettiCount; i++) {{
                    var p = particles[i];
                    ctx.beginPath();
                    ctx.lineWidth = p.r / 2;
                    ctx.strokeStyle = p.color;
                    ctx.moveTo(p.x + p.tilt + p.r / 4, p.y);
                    ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 4);
                    ctx.stroke();
                }}

                update();
                if (elapsed < 3000) {{
                    animationFrameId = requestAnimationFrame(draw);
                }} else {{
                    ctx.clearRect(0, 0, W, H);
                }}
            }}

            function update() {{
                for (var i = 0; i < confettiCount; i++) {{
                    var p = particles[i];
                    p.tiltAngle += p.tiltAngleIncremental;
                    p.y += (Math.cos(p.d) + 3 + p.r / 2) * 0.8;
                    p.x += Math.sin(p.d);
                    p.tilt = Math.sin(p.tiltAngle - (i / 3)) * 12;
                }}
            }}

            draw();
        }})();
        </script>
    </body>
    </html>
    """

    try:
        self.web.stdHtml(full_html, css=[], js=[], context=self)
    except TypeError:
        try:
            self.web.stdHtml(body=full_html, css=[], js=[], context=self)
        except Exception:
            self.web.setHtml(full_html)
