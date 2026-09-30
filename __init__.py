"""
AnkiBiotic - Main Entry Point & Hook Integrations
- Replaces DeckBrowser rendering with AnkiBiotic Dashboard
- Registers webview action handlers (pycmd)
- Adds Tools menu entry for Settings
"""

from typing import Any
from aqt import mw, gui_hooks
from aqt.deckbrowser import DeckBrowser
from aqt.overview import Overview
from aqt.qt import QAction

from .config import load_config
from .renderer import render_ankibiotic_deck_browser
from .settings import open_settings_dialog

def on_webview_cmd(handled: tuple, cmd: str, context: object) -> tuple:
    """
    Handle JavaScript pycmd events triggered from AnkiBiotic webview.
    """
    if not isinstance(context, (DeckBrowser, Overview)):
        return handled

    # --- Settings ---
    if cmd == "openAnkiBioticSettings":
        try:
            open_settings_dialog()
        except Exception as e:
            print(f"[AnkiBiotic] Settings error: {e}")
        return (True, None)

    # --- Add Cards ---
    if cmd == "add":
        try:
            mw.onAddCards()
        except Exception as e:
            print(f"[AnkiBiotic] Add cards error: {e}")
        return (True, None)

    # --- Browse ---
    if cmd == "browse":
        try:
            from aqt import dialogs
            dialogs.open("Browser", mw)
        except Exception as e:
            print(f"[AnkiBiotic] Browse error: {e}")
        return (True, None)

    # --- Stats ---
    if cmd == "stats":
        try:
            mw.onStats()
        except Exception as e:
            print(f"[AnkiBiotic] Stats error: {e}")
        return (True, None)

    # --- Sync ---
    if cmd == "sync":
        try:
            try:
                mw.on_sync_button_clicked()
            except AttributeError:
                mw.sync()
        except Exception as e:
            print(f"[AnkiBiotic] Sync error: {e}")
        return (True, None)

    # --- Create Deck ---
    if cmd in ("create", "createDeck", "ankibiotic:create_deck", "new_deck"):
        try:
            if hasattr(context, "_on_create"):
                context._on_create()
            elif hasattr(mw, "deckBrowser") and hasattr(mw.deckBrowser, "_on_create"):
                mw.deckBrowser._on_create()
            elif hasattr(mw, "onAddDeck"):
                mw.onAddDeck()
            else:
                from aqt.operations.deck import add_deck_dialog
                add_deck_dialog(parent=mw).run_in_background()
        except Exception as e:
            try:
                from aqt.operations.deck import add_deck_dialog
                add_deck_dialog(parent=mw)
            except Exception as ex2:
                print(f"[AnkiBiotic] Create deck error: {e}, {ex2}")
        return (True, None)

    # --- Import File ---
    if cmd in ("import", "ankibiotic:import_file", "import_file"):
        try:
            if hasattr(mw, "onImport"):
                mw.onImport()
            elif hasattr(context, "mw") and hasattr(context.mw, "onImport"):
                context.mw.onImport()
            elif hasattr(context, "_onImport"):
                context._onImport()
        except Exception as e:
            print(f"[AnkiBiotic] Import file error: {e}")
        return (True, None)

    # --- Get Shared Decks ---
    if cmd in ("shared", "getShared", "ankibiotic:get_shared", "get_shared"):
        try:
            if hasattr(context, "_onShared"):
                context._onShared()
            elif hasattr(mw, "deckBrowser") and hasattr(mw.deckBrowser, "_onShared"):
                mw.deckBrowser._onShared()
            else:
                import aqt
                from aqt.utils import openLink
                openLink(getattr(aqt, "appShared", "https://ankiweb.net/shared/") + "decks/")
        except Exception as e:
            try:
                from aqt.utils import openLink
                openLink("https://ankiweb.net/shared/decks/")
            except Exception as ex2:
                print(f"[AnkiBiotic] Get shared error: {e}, {ex2}")
        return (True, None)

    # --- Open Deck (study overview) ---
    if cmd.startswith("open:"):
        try:
            deck_id_str = cmd.split(":", 1)[1]
            deck_id = int(deck_id_str)
            mw.col.decks.select(deck_id)
            mw.onOverview()
        except Exception as e:
            print(f"[AnkiBiotic] Open deck error: {e}")
        return (True, None)

    # --- Toggle Deck (collapse/expand children) ---
    if cmd.startswith("toggle:"):
        try:
            deck_id_str = cmd.split(":", 1)[1]
            deck_id = int(deck_id_str)
            # Toggle via Anki's built-in collapse mechanism
            try:
                node = mw.col.decks.get(deck_id)
                if node:
                    current = node.get("collapsed", False)
                    node["collapsed"] = not current
                    mw.col.decks.save(node)
            except Exception:
                # Fallback: use sched API
                try:
                    mw.col.sched.set_deck_collapsed(deck_id, collapsed=not current if 'current' in dir() else True)
                except Exception:
                    pass
            # Refresh the deck browser to show the change
            if mw.deckBrowser:
                mw.deckBrowser.refresh()
        except Exception as e:
            print(f"[AnkiBiotic] Toggle deck error: {e}")
        return (True, None)

    # --- Deck Options ---
    if cmd.startswith("opts:"):
        try:
            deck_id_str = cmd.split(":", 1)[1]
            deck_id = int(deck_id_str)
            from aqt.qt import QTimer
            def _open_opts():
                try:
                    mw.col.decks.select(deck_id)
                    # Modern Anki API
                    try:
                        from aqt.operations.deck import set_deck_collapsed
                    except ImportError:
                        pass
                    try:
                        from aqt.deckconf import DeckConf
                        d = DeckConf(mw, mw.col.decks.get(deck_id))
                        d.exec()
                    except Exception:
                        # Fallback for newer Anki
                        try:
                            mw.onDeckConf(mw.col.decks.get(deck_id))
                        except Exception as ex2:
                            print(f"[AnkiBiotic] Deck opts inner error: {ex2}")
                except Exception as ex:
                    print(f"[AnkiBiotic] Deck opts inner error: {ex}")
            QTimer.singleShot(0, _open_opts)
        except Exception as e:
            print(f"[AnkiBiotic] Deck opts error: {e}")
        return (True, None)

    # --- Heatmap date search ---
    if cmd.startswith("ankibiotic_search_date:"):
        date_str = cmd.split(":", 1)[1]
        try:
            from datetime import date
            target_date = date.fromisoformat(date_str)
            today = date.today()
            diff_days = (today - target_date).days  # positive = days ago
            if diff_days >= 0:
                # rated:N finds cards rated in the last N days (1 = today, 2 = today + yesterday, etc.)
                query = f"rated:{max(diff_days + 1, 1)}"
            else:
                # Future dates: prop:due:N (N days from now)
                query = f"prop:due:{abs(diff_days)}"

            from aqt.qt import QTimer
            def _open_and_search():
                try:
                    from aqt import dialogs
                    browser = dialogs.open("Browser", mw)
                    if browser:
                        browser.search_for(query)
                except Exception as ex:
                    print(f"[AnkiBiotic] Browser open error: {ex}")
            QTimer.singleShot(0, _open_and_search)
            return (True, None)
        except Exception as e:
            print(f"[AnkiBiotic] Search error: {e}")
            return (True, None)

    return handled

def build_global_theme_css(theme_id: str) -> str:
    """Builds clean background CSS that matches the window and app pages to the theme without modifying card content."""
    from .config import load_config, get_theme_palette
    cfg = load_config()
    pal = get_theme_palette(theme_id)

    bg = pal.get("bg", "#1a120e")
    card_bg = pal.get("card_bg", "#241a13")
    card_inset = pal.get("card_inset", "#2e2119")
    border = pal.get("border", "#4a3729")
    fg = pal.get("fg", "#faecd0")
    fg_muted = pal.get("fg_muted", "#b89f8c")
    accent = pal.get("accent", "#d4a373")
    accent_hover = pal.get("accent_hover", "#e6be94")
    gold = pal.get("gold", "#f4c06b")

    return f"""
        :root, :root.night-mode, :root.nightMode, html, body {{
            --canvas: {bg} !important;
            --ab-bg: {bg};
            --ab-card-bg: {card_bg};
            --ab-card-inset: {card_inset};
            --ab-border: {border};
            --ab-fg: {fg};
            --ab-fg-muted: {fg_muted};
            --ab-accent: {accent};
            --ab-accent-hover: {accent_hover};
            --ab-gold: {gold};
        }}

        /* 1. Global Page Backgrounds (خلفية النوافذ والصفحات فقط - دون لمس البطاقة) */
        html, body, #outer, #main, .middle, .review-deck, .review-count,
        #qa, .nightMode #qa, #bottombar, .bottom-bar, #middle, #innertable {{
            background-color: {bg} !important;
            background: {bg} !important;
        }}

        /* 2. Top Toolbar Styling */
        #header, #header-inner, .toptoolbar, header {{
            background: {bg} !important;
            background-color: {bg} !important;
            border-color: {border} !important;
        }}
        .toolbar, body.fancy .toolbar, body.fancy:not(.flat) .toolbar {{
            background: {card_bg} !important;
            background-color: {card_bg} !important;
            border: 1px solid {border} !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08) !important;
        }}
        .hitem, body.fancy .hitem, body.fancy:not(.flat) .hitem, a.toplink, .toplink {{
            color: {fg} !important;
            background: transparent !important;
            border: none !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            padding: 5px 14px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            text-decoration: none !important;
            text-shadow: none !important;
        }}
        .hitem:hover, body.fancy .hitem:hover, a.toplink:hover, .toplink:hover {{
            background-color: {card_inset} !important;
            color: {accent} !important;
        }}

        /* 3. Overview Screen & Congratulations Screen Backgrounds */
        #congrats, .congrats, .finished, .overview, .studyoptions {{
            background-color: {bg} !important;
        }}

        /* Scrollbars */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {border};
            border-radius: 999px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {accent};
        }}
    """


def apply_theme_quick(theme_id: str) -> None:
    """Quickly switch theme and update all UI views instantly across Anki."""
    import base64
    from .config import load_config, save_config, invalidate_cache, get_theme_palette
    from aqt.qt import QColor

    invalidate_cache()
    cfg = load_config()
    cfg["theme"] = theme_id
    save_config(cfg)

    pal = get_theme_palette(theme_id)
    bg = pal.get("bg", "#1a120e")
    css = build_global_theme_css(theme_id)

    # 1. Update deckBrowser web background and DOM classes
    if mw and hasattr(mw, "deckBrowser") and mw.deckBrowser and mw.deckBrowser.web:
        try:
            mw.deckBrowser.web.page().setBackgroundColor(QColor(bg))
            js = f"""
            (function() {{
                var tc = 'theme-{theme_id}';
                var app = document.getElementById('ankibiotic-app') || document.querySelector('.ankibiotic-app');
                if (app) {{ app.className = 'ankibiotic-app ' + tc; app.setAttribute('data-theme', '{theme_id}'); }}
                if (document.body) {{ document.body.className = tc; document.body.setAttribute('data-theme', '{theme_id}'); }}
                if (document.documentElement) {{ document.documentElement.className = tc; document.documentElement.setAttribute('data-theme', '{theme_id}'); }}
            }})();
            """
            mw.deckBrowser.web.eval(js)
        except Exception:
            pass

    # Safe CSS injection snippet for WebViews
    css_b64 = base64.b64encode(css.encode("utf-8")).decode("ascii")
    inject_js = f"""
    (function() {{
        var st = document.getElementById('ankibiotic-global-page-theme');
        if (!st) {{
            st = document.createElement('style');
            st.id = 'ankibiotic-global-page-theme';
            document.head.appendChild(st);
        }}
        st.textContent = decodeURIComponent(escape(atob('{css_b64}')));
    }})();
    """

    # 2. Update Anki's Top Toolbar
    if mw and hasattr(mw, "toolbar") and mw.toolbar and mw.toolbar.web:
        try:
            mw.toolbar.web.page().setBackgroundColor(QColor(bg))
            mw.toolbar.web.eval(inject_js)
            try:
                mw.toolbar.draw()
            except Exception:
                pass
        except Exception as e:
            print(f"[AnkiBiotic] Toolbar styling error: {e}")

    # 3. Update Reviewer web and bottom bar if active
    if mw and hasattr(mw, "reviewer") and mw.reviewer:
        try:
            if hasattr(mw.reviewer, "web") and mw.reviewer.web:
                mw.reviewer.web.page().setBackgroundColor(QColor(bg))
                mw.reviewer.web.eval(inject_js)
            if hasattr(mw.reviewer, "bottom") and mw.reviewer.bottom and hasattr(mw.reviewer.bottom, "web") and mw.reviewer.bottom.web:
                mw.reviewer.bottom.web.page().setBackgroundColor(QColor(bg))
                mw.reviewer.bottom.web.eval(inject_js)
        except Exception as e:
            print(f"[AnkiBiotic] Reviewer styling error: {e}")

    # 4. Update Overview web if active
    if mw and hasattr(mw, "overview") and mw.overview and hasattr(mw.overview, "web") and mw.overview.web:
        try:
            mw.overview.web.page().setBackgroundColor(QColor(bg))
            mw.overview.web.eval(inject_js)
        except Exception:
            pass


def on_webview_will_set_content(web_content: Any, context: Any) -> None:
    """Injects AnkiBiotic theme styling across all Anki webviews (Overview, Reviewer, Bottom Bar, etc.)."""
    try:
        from .config import load_config
        cfg = load_config()
        if not cfg.get("enabled", True):
            return

        theme_id = cfg.get("theme", "coffee_mocha")
        css = build_global_theme_css(theme_id)
        theme_tag = f'<style id="ankibiotic-global-page-theme">{css}</style>'
        web_content.head += theme_tag
    except Exception as e:
        print(f"[AnkiBiotic] Global webview styling error: {e}")

def setup_menu():
    """Add dedicated AnkiBiotic top menu bar entry and Tools item."""
    from aqt.qt import QMenu
    from .config import get_day_themes, get_night_themes

    # 1. Dedicated Top Menu Bar Menu
    try:
        menu = QMenu("☕ AnkiBiotic", mw)
        
        act_settings = QAction("⚙️ لوحة الإعدادات والتحكم...", mw)
        act_settings.triggered.connect(open_settings_dialog)
        menu.addAction(act_settings)

        # Quick themes sub-menu with Day and Night categories
        theme_menu = QMenu("🎨 تغيير النمط فورياً", menu)

        day_menu = QMenu("☀️ الوضع النهاري", theme_menu)
        for tid, name in get_day_themes().items():
            t_action = QAction(name, day_menu)
            t_action.triggered.connect(lambda checked=False, t=tid: apply_theme_quick(t))
            day_menu.addAction(t_action)
        theme_menu.addMenu(day_menu)

        night_menu = QMenu("🌙 الوضع الليلي", theme_menu)
        for tid, name in get_night_themes().items():
            t_action = QAction(name, night_menu)
            t_action.triggered.connect(lambda checked=False, t=tid: apply_theme_quick(t))
            night_menu.addAction(t_action)
        theme_menu.addMenu(night_menu)

        menu.addMenu(theme_menu)

        menu.addSeparator()

        act_refresh = QAction("🔄 تحديث لوحة التحكم", mw)
        act_refresh.triggered.connect(lambda: mw.deckBrowser.refresh() if mw and mw.deckBrowser else None)
        menu.addAction(act_refresh)

        # Add to Anki's main top menubar
        mw.form.menubar.addMenu(menu)
    except Exception as e:
        print(f"[AnkiBiotic] Menubar error: {e}")

    # 2. Also keep entry in Tools menu for convenience
    try:
        action = QAction("إعدادات AnkiBiotic ☕", mw)
        action.triggered.connect(open_settings_dialog)
        mw.form.menuTools.addAction(action)
    except Exception:
        pass

def hide_anki_bottom_bar() -> None:
    """Completely hides and collapses the bottom webview when on the deck browser."""
    if not mw:
        return
    # Clear and detach any buttons from DeckBrowser bottom bar
    try:
        if hasattr(mw, "deckBrowser") and mw.deckBrowser and hasattr(mw.deckBrowser, "bottom") and mw.deckBrowser.bottom:
            mw.deckBrowser.bottom.draw("")
    except Exception:
        pass

    # Empty HTML, set height 0 and hide bottomWeb
    if hasattr(mw, "bottomWeb") and mw.bottomWeb:
        try:
            mw.bottomWeb.setHtml("<!DOCTYPE html><html><head><style>html,body{background:transparent;margin:0;padding:0;overflow:hidden;}</style></head><body></body></html>")
            mw.bottomWeb.setFixedHeight(0)
            mw.bottomWeb.setMaximumHeight(0)
            mw.bottomWeb.hide()
        except Exception:
            pass

def show_anki_bottom_bar() -> None:
    """Restores the bottom webview when entering review or overview."""
    if not mw or not hasattr(mw, "bottomWeb") or not mw.bottomWeb:
        return
    try:
        mw.bottomWeb.setMinimumHeight(0)
        mw.bottomWeb.setMaximumHeight(16777215)
        mw.bottomWeb.show()
    except Exception:
        pass

def patch_bottom_web() -> None:
    """Intercepts bottomWeb._onHeight so it never expands on the deck browser."""
    if not mw or not hasattr(mw, "bottomWeb") or not mw.bottomWeb:
        return
    if getattr(mw.bottomWeb, "_ankibiotic_patched", False):
        return

    orig_on_height = mw.bottomWeb._onHeight
    def _ankibiotic_on_height(height: Any) -> None:
        if getattr(mw, "state", "") == "deckBrowser":
            try:
                mw.bottomWeb.setFixedHeight(0)
                mw.bottomWeb.setMaximumHeight(0)
                mw.bottomWeb.hide()
            except Exception:
                pass
            return
        return orig_on_height(height)

    mw.bottomWeb._onHeight = _ankibiotic_on_height
    mw.bottomWeb._ankibiotic_patched = True

def enable_ankibiotic():
    """Apply DeckBrowser replacement."""
    try:
        cfg = load_config()
        if cfg.get("enabled", True):
            DeckBrowser._renderPage = render_ankibiotic_deck_browser
            try:
                from .congrats_renderer import render_ankibiotic_congrats
                Overview._show_finished_screen = render_ankibiotic_congrats
            except Exception as ex_ov:
                print(f"[AnkiBiotic] Overview finished screen hook error: {ex_ov}")
            print("[AnkiBiotic] Initialized successfully. DeckBrowser and Victory Screen active.")

            patch_bottom_web()
            hide_anki_bottom_bar()

            if mw and hasattr(mw, "deckBrowser") and mw.deckBrowser:
                mw.deckBrowser.show()

            # Apply full theme to toolbar and background shortly after init
            from aqt.qt import QTimer
            theme_id = cfg.get("theme", "coffee_mocha")
            QTimer.singleShot(200, lambda: apply_theme_quick(theme_id))

            # Safety patch: prevent AssertionError when Edit Current is invoked without active card
            if hasattr(mw, "onEditCurrent"):
                orig_edit_current = mw.onEditCurrent
                def _safe_edit_current(*args, **kwargs):
                    if not getattr(mw, "reviewer", None) or not getattr(mw.reviewer, "card", None):
                        return
                    try:
                        return orig_edit_current(*args, **kwargs)
                    except AssertionError:
                        pass
                    except Exception as ex:
                        print(f"[AnkiBiotic] Handled edit current safely: {ex}")
                mw.onEditCurrent = _safe_edit_current
    except Exception as e:
        print(f"[AnkiBiotic] Error during initialization: {e}")

def on_state_will_change(new_state: str, old_state: str) -> None:
    """Invoked before view state changes."""
    if new_state == "deckBrowser":
        hide_anki_bottom_bar()
    elif new_state in ("review", "overview"):
        show_anki_bottom_bar()

def on_state_did_change(new_state: str, old_state: str) -> None:
    """Triggered when Anki changes view state (e.g. returning from review to deckBrowser)."""
    if new_state == "deckBrowser":
        hide_anki_bottom_bar()
        try:
            cfg = load_config()
            apply_theme_quick(cfg.get("theme", "coffee_mocha"))
        except Exception:
            pass
    elif new_state in ("review", "overview"):
        show_anki_bottom_bar()

def on_reviewer_will_end() -> None:
    """Invoked when reviewer session ends."""
    hide_anki_bottom_bar()

def init_addon():
    """Main initialization method."""
    gui_hooks.main_window_did_init.append(enable_ankibiotic)
    gui_hooks.main_window_did_init.append(setup_menu)
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    gui_hooks.state_will_change.append(on_state_will_change)
    gui_hooks.state_did_change.append(on_state_did_change)
    gui_hooks.reviewer_will_end.append(on_reviewer_will_end)
    gui_hooks.webview_did_receive_js_message.append(on_webview_cmd)

# Execute immediately on module import
init_addon()
