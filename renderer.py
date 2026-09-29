"""
AnkiBiotic - Dashboard Renderer
Assembles Dashboard (Left) + Sidebar (Right), Live Stats,
52-Week Heatmap, Coffee Mocha & Multi-Themes, Goals, ETA,
Badges Strip, Day Details Modal, and Deck Tree.
"""

import os
import json
import html
from aqt import mw
from aqt.deckbrowser import DeckBrowser

from .config import load_config, get_user_avatar_html, get_font_info
from .stats_engine import get_stats_data, calculate_eta, compute_badges
from .heatmap_engine import get_ankibiotic_heatmap_data
from .deck_tree import build_ankibiotic_deck_tree
from .i18n import get_t

def get_avatar_svg() -> str:
    """Returns elegant gold-accented avatar SVG."""
    return """
    <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
        <circle cx="50" cy="38" r="16" fill="var(--ab-gold)"/>
        <path d="M26 78C26 64.7452 36.7452 54 50 54C63.2548 54 74 64.7452 74 78V84H26V78Z" fill="var(--ab-accent)"/>
    </svg>
    """

def render_ankibiotic_deck_browser(self: DeckBrowser, reuse: bool = False) -> None:
    """
    Primary entry point replacing DeckBrowser._renderPage with AnkiBiotic Dashboard.
    """
    # 1. Clear any contents in DeckBrowser's bottom bar and detach previous handlers
    if hasattr(self, "bottom") and self.bottom:
        try:
            self.bottom.draw("")
        except Exception:
            pass

    # 2. Force collapse and hide mw.bottomWeb
    if mw and hasattr(mw, "bottomWeb") and mw.bottomWeb:
        try:
            mw.bottomWeb.setHtml("<!DOCTYPE html><html><head><style>html,body{background:transparent;margin:0;padding:0;overflow:hidden;}</style></head><body></body></html>")
            mw.bottomWeb.setFixedHeight(0)
            mw.bottomWeb.setMaximumHeight(0)
            mw.bottomWeb.hide()
        except Exception:
            pass

    cfg = load_config()
    lang = cfg.get("language", "ar")
    t = get_t(lang)

    stats = get_stats_data(lang=lang)
    heatmap_data = get_ankibiotic_heatmap_data()
    heatmap_data["lang"] = lang

    # Base web assets path
    addon_dir = os.path.dirname(__file__)
    css_path = os.path.join(addon_dir, "web", "style.css")
    js_path = os.path.join(addon_dir, "web", "ankibiotic.js")

    css_content = ""
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
        except Exception:
            pass

    js_content = ""
    if os.path.exists(js_path):
        try:
            with open(js_path, "r", encoding="utf-8") as f:
                js_content = f.read()
        except Exception:
            pass

    # Dynamic Deck Tree with localization
    deck_tree_html = build_ankibiotic_deck_tree(lang=lang)

    # User profile metadata
    default_name = "المستخدم" if lang == "ar" else "User"
    default_sub = "طالب علم ومراجع متميز" if lang == "ar" else "Avid Scholar & Continuous Learner"
    user_name = html.escape(cfg.get("user_name", default_name))
    profile_subtitle = html.escape(cfg.get("profile_subtitle", default_sub))
    avatar_html = get_user_avatar_html(cfg)

    # Theme body class
    theme = cfg.get('theme', 'coffee_mocha')
    body_class = f'theme-{theme}'

    # Total due across all types
    total_due = stats.get('due_count', 0) + stats.get('new_count', 0) + stats.get('learn_count', 0)

    # Configurable Quick Nav Bar
    quick_nav_html = ""
    if cfg.get("show_quick_nav", True):
        quick_nav_html = f"""
                <!-- Quick Navigation Bar -->
                <div class="quick-nav-bar">
                    <button class="quick-btn" onclick="pycmd('browse')" title="{t['browse_title']}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                        <span>{t['browse']}</span>
                    </button>
                    <button class="quick-btn" onclick="pycmd('stats')" title="{t['stats_title']}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                        </svg>
                        <span>{t['stats']}</span>
                    </button>
                    <button class="quick-btn" onclick="pycmd('sync')" title="{t['sync_title']}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="23 4 23 10 17 10"></polyline>
                            <polyline points="1 20 1 14 7 14"></polyline>
                            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                        </svg>
                        <span>{t['sync']}</span>
                    </button>
                    <button class="quick-btn" onclick="pycmd('openAnkiBioticSettings')" title="{t['settings_title']}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="3"></circle>
                            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                        </svg>
                        <span>{t['settings']}</span>
                    </button>
                </div>
        """

    # Configurable Streak Badge
    show_streak = cfg.get("show_streak", True)
    streak_header_html = f"""
                    <div class="header-status-pill">
                        <span class="status-dot"></span>
                        <span>🔥 {stats['streak']} {t['streak_pill']}</span>
                    </div>
    """ if show_streak else ""

    # Estimated Finish Time (ETA)
    show_eta = cfg.get("show_eta", True)
    eta_header_html = ""
    if show_eta:
        eta_info = calculate_eta(stats, lang=lang)
        eta_header_html = f"""
                    <div class="header-status-pill eta-pill" title="{eta_info.get('display_text', '')}">
                        <span>{eta_info.get('display_text', '')}</span>
                    </div>
        """

    streak_footer_html = f"""
                        <div class="streak-badge">
                            <span>🔥 {t['streak_label']}{stats['streak']} {t['days']}</span>
                        </div>
    """ if show_streak else ""

    # Daily Study Goal & Progress
    goal_html = ""
    if cfg.get("daily_goal_enabled", True):
        goal_target = int(cfg.get("daily_goal_cards", 100))
        studied = stats.get("studied", 0)
        pct = min(100, int((studied / goal_target) * 100)) if goal_target > 0 else 100
        is_achieved = studied >= goal_target and goal_target > 0
        achieved_badge = f'<div class="goal-achieved-badge">{t["goal_achieved"]}</div>' if is_achieved else ""
        progress_text = t["goal_progress"].format(studied=studied, goal=goal_target, percent=pct)
        goal_html = f"""
                <!-- Daily Study Goal Card -->
                <section class="daily-goal-card {'goal-completed' if is_achieved else ''}">
                    <div class="goal-card-header">
                        <div class="goal-title-group">
                            <span class="goal-icon">🎯</span>
                            <span class="goal-title">{t['goal_title']}</span>
                        </div>
                        <span class="goal-percentage">{pct}%</span>
                    </div>
                    <div class="goal-progress-wrap">
                        <div class="goal-bar-bg">
                            <div class="goal-bar-fill" style="width: {pct}%;"></div>
                        </div>
                    </div>
                    <div class="goal-footer">
                        <span class="goal-progress-text">{progress_text}</span>
                        {achieved_badge}
                    </div>
                </section>
        """

    # Achievements & Badges Strip
    badges_list = compute_badges(stats, total_reviews_ever=heatmap_data.get("total_reviews", 0), lang=lang)
    unlocked_count = sum(1 for b in badges_list if b["unlocked"])
    badges_items = []
    for b in badges_list:
        cls = "badge-item-unlocked" if b["unlocked"] else "badge-item-locked"
        lock_icon = "" if b["unlocked"] else '<span class="lock-overlay">🔒</span>'
        tooltip = f"{b['title']} - {b['desc']} ({b['progress_str']})"
        badges_items.append(f"""
            <div class="badge-mini-item {cls}" title="{html.escape(tooltip)}">
                <span class="badge-mini-icon">{b['icon']}</span>
                {lock_icon}
                <span class="badge-mini-title">{html.escape(b['title'])}</span>
            </div>
        """)

    badges_strip_html = f"""
                <!-- Badges & Achievements Strip -->
                <section class="badges-strip-card">
                    <div class="badges-header">
                        <div class="badges-title">
                            <span>🏆 {t['badges_title']}</span>
                            <span class="badges-count-pill">{unlocked_count}/{len(badges_list)} {t['badges_unlocked']}</span>
                        </div>
                        <button class="badges-config-btn" onclick="pycmd('openAnkiBioticSettings')" title="{t['settings']}">⚙️</button>
                    </div>
                    <div class="badges-grid-mini">
                        {''.join(badges_items)}
                    </div>
                </section>
    """

    # Configurable Live Metrics
    stat_cards = []
    if cfg.get("show_stat_studied", True):
        stat_cards.append(f"""
                    <!-- 1. Studied -->
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <span class="stat-card-label">{t['stat_studied_title']}</span>
                            <div class="stat-card-icon icon-studied">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="stat-card-value">{stats['studied']}</div>
                        <div class="stat-card-sub">
                            <span class="sub-new">● {t['stat_new']}: {stats['new_count']}</span>
                            <span class="sub-sep">|</span>
                            <span class="sub-learn">● {t['stat_learn']}: {stats['learn_count']}</span>
                            <span class="sub-sep">|</span>
                            <span class="sub-due">● {t['stat_due']}: {stats['due_count']}</span>
                        </div>
                    </div>
        """)

    if cfg.get("show_stat_retention", True):
        stat_cards.append(f"""
                    <!-- 2. Retention -->
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <span class="stat-card-label">{t['stat_retention_title']}</span>
                            <div class="stat-card-icon icon-retention">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                                </svg>
                            </div>
                        </div>
                        <div class="stat-card-value">{stats['retention']}</div>
                        <div class="stat-card-sub">
                            <span>{t['stat_retention_sub']}</span>
                        </div>
                    </div>
        """)

    if cfg.get("show_stat_pace", True):
        stat_cards.append(f"""
                    <!-- 3. Pace -->
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <span class="stat-card-label">{t['stat_pace_title']}</span>
                            <div class="stat-card-icon icon-pace">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <polyline points="12 6 12 12 16 14"></polyline>
                                </svg>
                            </div>
                        </div>
                        <div class="stat-card-value">{stats['pace_sec_per_card']} <span class="stat-unit">{t['stat_pace_unit']}</span></div>
                        <div class="stat-card-sub">
                            <span>{stats['pace_cards_per_sec']} {t['stat_pace_sub']}</span>
                        </div>
                    </div>
        """)

    if cfg.get("show_stat_time", True):
        stat_cards.append(f"""
                    <!-- 4. Time -->
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <span class="stat-card-label">{t['stat_time_title']}</span>
                            <div class="stat-card-icon icon-time">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                                </svg>
                            </div>
                        </div>
                        <div class="stat-card-value">{stats['time_formatted']}</div>
                        <div class="stat-card-sub">
                            <span>{t['stat_time_sub']}</span>
                        </div>
                    </div>
        """)

    stats_grid_html = ""
    if stat_cards:
        stats_grid_html = f"""
                <!-- Live Metrics Grid -->
                <section class="stats-grid">
                    {''.join(stat_cards)}
                </section>
        """

    # Heatmap default view & buttons state
    default_view = cfg.get("default_heatmap_view", "year")
    start_of_week = cfg.get("start_of_week", "sunday")
    heatmap_data["default_view"] = default_view
    heatmap_data["start_of_week"] = start_of_week

    btn_active_week = " active" if default_view == "week" else ""
    btn_active_month = " active" if default_view == "month" else ""
    btn_active_year = " active" if default_view == "year" else ""

    # Appearance options
    card_radius = int(cfg.get("card_radius", 16))
    card_opacity = float(cfg.get("card_opacity", 0.94))
    font_key = cfg.get("font_family_preset", "cairo")
    font_info = get_font_info(font_key)
    font_css = font_info.get("css", "'Cairo', 'Segoe UI', Tahoma, sans-serif")
    google_font_url = f"https://fonts.googleapis.com/css2?family={font_info['google']}&display=swap" if font_info.get("google") else ""
    google_font_tag = f'<link rel="stylesheet" href="{google_font_url}">' if google_font_url else ""
    ui_scale = float(cfg.get("ui_scale", 100)) / 100.0

    # Heatmap Day Details Modal
    day_modal_html = f"""
        <!-- Heatmap Day Details Modal -->
        <div id="ankibiotic-day-modal" class="hm-day-modal-overlay" style="display:none;" onclick="if(event.target===this) AnkiBiotic.closeDayModal();">
            <div class="hm-day-modal-card">
                <div class="hm-modal-header">
                    <h3 id="hm-modal-date-title">{t['day_details_title']}</h3>
                    <button class="hm-modal-close-btn" onclick="AnkiBiotic.closeDayModal()">✕</button>
                </div>
                <div class="hm-modal-body">
                    <div class="hm-modal-count-row">
                        <span class="hm-modal-count-val" id="hm-modal-count-val">0</span>
                        <span class="hm-modal-count-label">{t['day_details_reviews']}</span>
                    </div>
                    <div class="hm-modal-level-tag" id="hm-modal-level-tag"></div>
                    <p class="hm-modal-desc" id="hm-modal-desc"></p>
                </div>
                <div class="hm-modal-footer">
                    <button class="hm-modal-browse-btn" id="hm-modal-browse-btn">
                        <span>{t['day_details_browse_btn']}</span>
                    </button>
                </div>
            </div>
        </div>
    """

    # Assemble HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html lang="{lang}" dir="{t['dir']}" class="{body_class} lang-{lang}" data-theme="{theme}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t['app_title']}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        {google_font_tag}
        <style>
            :root, body, html {{
                --ab-radius: {card_radius}px !important;
                --ab-card-opacity: {card_opacity} !important;
                --ab-font-family: {font_css} !important;
                --ab-zoom: {ui_scale} !important;
            }}
            body {{
                font-family: var(--ab-font-family) !important;
                zoom: var(--ab-zoom, 1);
            }}
            {css_content}
        </style>
    </head>
    <body class="{body_class} lang-{lang}" data-theme="{theme}">
        <div class="ankibiotic-app {body_class} lang-{lang}" id="ankibiotic-app" data-theme="{theme}">

            <!-- SIDEBAR -->
            <aside class="ankibiotic-sidebar">

                <!-- Profile Card -->
                <div class="profile-section">
                    <div class="profile-avatar-box">
                        {avatar_html}
                    </div>
                    <div class="profile-meta">
                        <h2>{user_name}</h2>
                        <p>{profile_subtitle}</p>
                    </div>
                </div>

                <!-- Add Card CTA Button -->
                <button class="add-card-btn" onclick="pycmd('add')">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    <span>{t['add_card_btn']}</span>
                </button>

                {quick_nav_html}

                <!-- Decks Panel -->
                <div class="decks-panel">
                    <div class="decks-panel-header">
                        <h3>{t['decks_title']}</h3>
                        <span class="badge badge-due">{total_due} {t['due_badge']}</span>
                    </div>
                    <div class="deck-scroll-list" id="ankibiotic-deck-tree">
                        {deck_tree_html}
                    </div>
                </div>

            </aside>

            <!-- MAIN: DASHBOARD -->
            <main class="ankibiotic-dashboard">

                <header class="dashboard-header">
                    <div class="dashboard-title-group">
                        <h1>
                            <span>{t['app_title']}</span>
                            <span class="coffee-badge">☕</span>
                        </h1>
                        <p class="dashboard-subtitle">{t['app_subtitle']}</p>
                    </div>
                    <div class="header-pills-row">
                        {streak_header_html}
                        {eta_header_html}
                    </div>
                </header>

                {goal_html}

                {stats_grid_html}

                {badges_strip_html}

                <!-- 52-Week Heatmap Card -->
                <section class="heatmap-card">
                    <div class="heatmap-card-header">
                        <div class="heatmap-title-box">
                            <h3>
                                <span>{t['heatmap_title']}</span>
                                <span class="heatmap-year-label" id="ankibiotic-period-label">({t['year_52w']})</span>
                            </h3>
                            <p>{t['heatmap_sub']}</p>
                        </div>
                        <div class="heatmap-header-actions">
                            <button class="hm-today-btn" id="hm-today-btn" style="display:none;" title="{t['return_today']}">{t['return_today']}</button>
                            <div class="heatmap-nav-controls">
                                <button class="heatmap-nav-btn{btn_active_week}" data-view="week">{t['week']}</button>
                                <button class="heatmap-nav-btn{btn_active_month}" data-view="month">{t['month']}</button>
                                <button class="heatmap-nav-btn{btn_active_year}" data-view="year">{t['year']}</button>
                            </div>
                        </div>
                    </div>

                    <!-- Navigation Wrapper with Side Arrows -->
                    <div class="heatmap-table-container">
                        <button class="hm-arrow-btn hm-arrow-prev" id="hm-prev-btn" title="{t['prev_period']}" aria-label="{t['prev_period']}">
                            <span class="hm-arrow-symbol">‹</span>
                        </button>

                        <div class="heatmap-grid-scroll" id="ankibiotic-heatmap-scroll">
                            <div id="ankibiotic-month-row" class="hm-month-row"></div>
                            <div class="heatmap-matrix" id="ankibiotic-heatmap-matrix"></div>
                        </div>

                        <button class="hm-arrow-btn hm-arrow-next disabled" id="hm-next-btn" title="{t['next_period']}" aria-label="{t['next_period']}" disabled>
                            <span class="hm-arrow-symbol">›</span>
                        </button>
                    </div>

                    <div class="heatmap-footer">
                        <div class="heatmap-legend">
                            <span>{t['hm_less']}</span>
                            <div class="legend-cell" data-level="0"></div>
                            <div class="legend-cell" data-level="1"></div>
                            <div class="legend-cell" data-level="2"></div>
                            <div class="legend-cell" data-level="3"></div>
                            <div class="legend-cell" data-level="4"></div>
                            <span>{t['hm_more']}</span>
                        </div>
                        <div class="heatmap-total">
                            <span id="hm-total-period-label">{t['hm_total_prefix']}</span>
                            <strong id="hm-total-period-revs">{heatmap_data['total_reviews']}</strong>
                        </div>
                        {streak_footer_html}
                    </div>
                </section>

            </main>

        </div>

        {day_modal_html}

        <script>
            window.ANKIBIOTIC_HEATMAP_DATA = {json.dumps(heatmap_data)};
            window.ANKIBIOTIC_STATS = {json.dumps(stats)};
            window.ANKIBIOTIC_LANG = "{lang}";
            {js_content}
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
