"""
AnkiBiotic - Heatmap generator with 52-week activity map,
streaks, and week/month/year navigation data.
"""

from typing import Dict, Any, List
from datetime import date, timedelta
from aqt import mw

def get_ankibiotic_heatmap_data() -> Dict[str, Any]:
    """
    Builds heatmap dataset representing 52 weeks of review activity.
    Returns:
    - days: List of {date: 'YYYY-MM-DD', count: N, level: 0-4, weekday: N}
    - streak: int
    - total_reviews_year: int
    - max_reviews_day: int
    - start_date: str
    - end_date: str
    - start_weekday: int  (Python weekday of start_date, 0=Mon, 6=Sun)
    """
    if not mw or not mw.col:
        return {
            "calendar": {},
            "days_list": [],
            "streak": 0,
            "total_reviews": 0,
            "max_reviews": 0,
            "today": date.today().isoformat(),
            "start_date": (date.today() - timedelta(days=364)).isoformat(),
            "start_weekday": 0,
        }

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

        # 52 weeks = 364 days back from today
        today_date = date.today()
        start_date = today_date - timedelta(days=364)

        # Query all reviews grouped by day correctly for full historical navigation
        query = """
            SELECT
                STRFTIME('%Y-%m-%d', (id / 1000) - ?, 'unixepoch', 'localtime') as day_key,
                COUNT() as cnt
            FROM revlog
            WHERE type IN (0,1,2,3)
            GROUP BY day_key
            ORDER BY day_key ASC
        """
        rows = col.db.all(query, rollover_sec)

        calendar = {row[0]: row[1] for row in rows if row[0]}

        # Calculate max and total
        total_revs = sum(calendar.values())
        max_rev = max(calendar.values()) if calendar else 0

        # Build daily map for past 52 weeks (364 days + today)
        daily_list = []
        curr = start_date
        while curr <= today_date:
            d_str = curr.isoformat()
            cnt = calendar.get(d_str, 0)

            # Level 0 to 4 based on density
            if cnt == 0:
                lvl = 0
            elif cnt <= 15:
                lvl = 1
            elif cnt <= 45:
                lvl = 2
            elif cnt <= 100:
                lvl = 3
            else:
                lvl = 4

            daily_list.append({
                "date": d_str,
                "count": cnt,
                "level": lvl,
                "weekday": curr.weekday()  # 0 = Monday, 6 = Sunday
            })
            curr += timedelta(days=1)

        from .stats_engine import compute_review_streak
        streak = compute_review_streak()

        return {
            "calendar": calendar,
            "days_list": daily_list,
            "streak": streak,
            "total_reviews": total_revs,
            "max_reviews": max_rev,
            "today": today_date.isoformat(),
            "start_date": start_date.isoformat(),
            "start_weekday": start_date.weekday(),
        }
    except Exception as e:
        print(f"[AnkiBiotic] Error generating heatmap data: {e}")
        return {
            "calendar": {},
            "days_list": [],
            "streak": 0,
            "total_reviews": 0,
            "max_reviews": 0,
            "today": date.today().isoformat(),
            "start_weekday": 0,
        }
