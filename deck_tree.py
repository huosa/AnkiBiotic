"""
AnkiBiotic - Deck Tree Builder with collapse/expand,
action shortcuts, and colored count indicators.
"""

import html
from typing import Any, List
from aqt import mw

def build_ankibiotic_deck_tree(lang: str = "ar") -> str:
    """
    Renders the collection's deck hierarchy with collapsible sub-decks.
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

    if not mw or not mw.col:
        return f"<div class='no-decks'>{t.get('no_decks', 'لا توجد رزم متوفرة')}</div>"

    try:
        try:
            from .config import load_config
        except (ImportError, ValueError):
            from config import load_config
        cfg = load_config()
        default_collapsed = cfg.get("decks_default_collapsed", False)
        try:
            tree = mw.col.sched.deck_due_tree()
        except AttributeError:
            tree = mw.col.decks.deck_tree()
        return _render_node_children(tree.children, depth=0, default_collapsed=default_collapsed, t=t)
    except Exception as e:
        print(f"[AnkiBiotic] Error rendering deck tree: {e}")
        return f"<div class='error-msg'>Error: {html.escape(str(e))}</div>"


def _render_node_children(children: List[Any], depth: int = 0, default_collapsed: bool = False, t: dict = None) -> str:
    if t is None:
        try:
            from .i18n import get_t
        except (ImportError, ValueError):
            from i18n import get_t
        t = get_t("ar")


    html_parts = []
    for node in children:
        deck_id = node.deck_id
        deck_name = html.escape(node.name)
        new_cnt = getattr(node, 'new_count', 0)
        learn_cnt = getattr(node, 'learn_count', 0)
        review_cnt = getattr(node, 'review_count', 0)
        total_due = new_cnt + learn_cnt + review_cnt

        has_children = bool(node.children)
        collapsed = getattr(node, 'collapsed', False) or default_collapsed

        indent_px = depth * 10
        depth_class = f"depth-{min(depth, 3)}"

        # Toggle arrow for parent decks
        toggle_html = ""
        if has_children:
            arrow_cls = "collapsed" if collapsed else "expanded"
            toggle_html = f'''<span class="deck-toggle {arrow_cls}"
                onclick="event.stopPropagation(); pycmd('toggle:{deck_id}')">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2.5"
                     stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
            </span>'''
        else:
            toggle_html = '<span class="deck-toggle-spacer"></span>'

        # Counts badges
        badges = []
        if new_cnt > 0:
            badges.append(f'<span class="badge badge-new" title="{t.get("stat_new", "جديدة")}">{new_cnt}</span>')
        if learn_cnt > 0:
            badges.append(f'<span class="badge badge-learn" title="{t.get("stat_learn", "تعلم")}">{learn_cnt}</span>')
        if review_cnt > 0:
            badges.append(f'<span class="badge badge-due" title="{t.get("stat_due", "مستحقة")}">{review_cnt}</span>')
        if total_due == 0:
            badges.append('<span class="badge badge-zero">✓</span>')
        badges_html = "\n".join(badges)

        due_class = "has-due" if total_due > 0 else "no-due"
        pad_style = f"padding-inline-start: {indent_px + 10}px;"

        item_html = f'''
        <div class="deck-row {due_class} {depth_class}"
             data-deck-id="{deck_id}"
             style="{pad_style}">
            {toggle_html}
            <div class="deck-info" onclick="pycmd('open:{deck_id}')">
                <span class="deck-folder-icon">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                    </svg>
                </span>
                <span class="deck-title" title="{deck_name}">{deck_name}</span>
            </div>
            <div class="deck-counts">
                {badges_html}
            </div>
            <div class="deck-actions-btn"
                 onclick="event.stopPropagation(); pycmd('opts:{deck_id}')"
                 title="{t.get('deck_opts', 'خيارات الرزمة')}">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="5" r="1.5"></circle>
                    <circle cx="12" cy="12" r="1.5"></circle>
                    <circle cx="12" cy="19" r="1.5"></circle>
                </svg>
            </div>
        </div>
        '''
        html_parts.append(item_html)

        # Render nested children
        if has_children:
            display = "none" if collapsed else "block"
            html_parts.append(
                f'<div class="deck-sub-tree" data-parent="{deck_id}" style="display:{display};">' +
                _render_node_children(node.children, depth + 1, default_collapsed, t=t) +
                '</div>'
            )

    return "\n".join(html_parts)

