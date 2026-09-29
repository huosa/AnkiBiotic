"""
AnkiBiotic - Modern Advanced Settings Dialog
Tabbed layout: Themes & Palette, Profile & Avatar, Heatmap & Stats, Layout & Decks.
"""

import os
from typing import Dict
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QGroupBox,
    QFormLayout, QMessageBox, Qt, QFrame, QTabWidget, QWidget,
    QCheckBox, QFileDialog, QScrollArea, QGridLayout, QButtonGroup,
    QColor, QStackedWidget
)
from aqt import mw
from .config import (
    load_config, save_config, invalidate_cache,
    reset_config, get_available_themes, get_day_themes, get_night_themes,
    is_theme_light, get_theme_palette, THEME_PALETTES, AVATAR_PRESETS,
    get_available_fonts, AVATAR_CATEGORIES, get_avatar_categories
)
from .stats_engine import get_stats_data, compute_badges
from .heatmap_engine import get_ankibiotic_heatmap_data
from .i18n import get_t


class AnkiBioticSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("⚙️ إعدادات وتخصيص AnkiBiotic")
        self.setMinimumWidth(720)
        self.setMinimumHeight(660)
        self.resize(760, 720)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.cfg = load_config()
        self.selected_theme = self.cfg.get("theme", "coffee_mocha")
        self.selected_avatar = self.cfg.get("avatar_type", "default")
        self.custom_avatar_path = self.cfg.get("custom_avatar_path", "")
        self.current_theme_mode = "day" if is_theme_light(self.selected_theme) else "night"
        self.selected_avatar_category = "all"

        self.theme_buttons = {}
        self.avatar_buttons = {}
        self.avatar_category_buttons = {}

        self.setup_ui()

        self.apply_dialog_theme(self.selected_theme)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(18, 18, 18, 18)

        # Header Title Banner
        banner = QHBoxLayout()
        title_box = QVBoxLayout()
        lbl_title = QLabel("🎨 لوحة تحكم وإعدادات AnkiBiotic")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: 800; color: inherit;")
        lbl_sub = QLabel("خصص المظهر، الألوان، خريطة المراجعة، والملف الشخصي حسب تفضيلاتك")
        lbl_sub.setStyleSheet("font-size: 11px; opacity: 0.8;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        banner.addLayout(title_box)
        banner.addStretch()
        main_layout.addLayout(banner)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Add 6 Tabs
        self.tab_theme = self.create_theme_tab()
        self.tab_general = self.create_general_tab()
        self.tab_profile = self.create_profile_tab()
        self.tab_heatmap = self.create_heatmap_tab()
        self.tab_badges = self.create_badges_tab()
        self.tab_layout = self.create_layout_tab()

        self.tabs.addTab(self.tab_theme, "🎨 الأنماط والألوان")
        self.tabs.addTab(self.tab_general, "🎯 الأهداف واللغة والخطوط")
        self.tabs.addTab(self.tab_profile, "👤 الملف الشخصي")
        self.tabs.addTab(self.tab_heatmap, "📊 خريطة النشاط والإحصائيات")
        self.tabs.addTab(self.tab_badges, "🏆 الشارات والإنجازات")
        self.tabs.addTab(self.tab_layout, "🎛️ تخصيص الواجهة والرزم")

        main_layout.addWidget(self.tabs)


        # ── Bottom Action Buttons ──
        btn_layout = QHBoxLayout()

        btn_reset = QPushButton("🔄 إعادة الضبط الافتراضي")
        btn_reset.setObjectName("btn_reset")
        btn_reset.setStyleSheet("color: #e06666; font-weight: bold;")
        btn_reset.clicked.connect(self.reset_defaults)

        btn_cancel = QPushButton("إلغاء")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("💾 حفظ وتطبيق التغييرات")
        btn_save.setObjectName("btn_save")
        btn_save.setStyleSheet("font-weight: 800; padding: 10px 22px;")
        btn_save.clicked.connect(self.save)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        main_layout.addLayout(btn_layout)

    # ============================================================
    # TAB 1: THEMES & PALETTES
    # ============================================================
    def create_theme_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(14, 14, 14, 14)

        lbl_info = QLabel("اختر النمط اللوني المناسب لبيئة دراستك (مقسم بين الوضع النهاري والوضع الليلي):")
        lbl_info.setStyleSheet("font-weight: 700; font-size: 12px;")
        layout.addWidget(lbl_info)

        # ── Mode Switcher Segmented Buttons ──
        mode_btn_box = QHBoxLayout()
        mode_btn_box.setSpacing(8)

        day_count = len(get_day_themes())
        night_count = len(get_night_themes())
        self.btn_day_mode = QPushButton(f"☀️ الوضع النهاري ({day_count} أنماط)")
        self.btn_day_mode.setFixedHeight(38)
        self.btn_day_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_day_mode.clicked.connect(lambda: self.switch_theme_mode("day"))

        self.btn_night_mode = QPushButton(f"🌙 الوضع الليلي ({night_count} أنماط)")
        self.btn_night_mode.setFixedHeight(38)
        self.btn_night_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_night_mode.clicked.connect(lambda: self.switch_theme_mode("night"))

        mode_btn_box.addWidget(self.btn_day_mode)
        mode_btn_box.addWidget(self.btn_night_mode)
        layout.addLayout(mode_btn_box)

        # ── Stacked Grids for Day and Night Modes ──
        self.theme_stack = QStackedWidget()

        # Page 0: Day Themes
        page_day = self._create_theme_grid_page(get_day_themes())
        self.theme_stack.addWidget(page_day)

        # Page 1: Night Themes
        page_night = self._create_theme_grid_page(get_night_themes())
        self.theme_stack.addWidget(page_night)

        layout.addWidget(self.theme_stack)

        # ── Appearance Properties ──
        grp_card = QGroupBox("✨ خصائص مظهر البطاقات وتنعيم الحواف")
        form_card = QFormLayout(grp_card)
        form_card.setSpacing(10)

        self.spn_radius = QSpinBox()
        self.spn_radius.setRange(0, 36)
        self.spn_radius.setValue(int(self.cfg.get("card_radius", 16)))
        self.spn_radius.setSuffix(" px")
        form_card.addRow("تنعيم الحواف وانحناء زوايا البطاقات (Border Radius):", self.spn_radius)

        self.spn_opacity = QDoubleSpinBox()
        self.spn_opacity.setRange(0.60, 1.0)
        self.spn_opacity.setSingleStep(0.02)
        self.spn_opacity.setDecimals(2)
        self.spn_opacity.setValue(float(self.cfg.get("card_opacity", 0.94)))
        form_card.addRow("شفافية البطاقات (Card Opacity):", self.spn_opacity)

        layout.addWidget(grp_card)

        # Select initial mode page matching selected theme
        initial_mode = "day" if is_theme_light(self.selected_theme) else "night"
        self.switch_theme_mode(initial_mode)
        self._update_theme_cards_state()
        return widget

    def _create_theme_grid_page(self, themes_dict: Dict[str, str]) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        if scroll.viewport():
            scroll.viewport().setStyleSheet("background-color: transparent; background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        grid = QGridLayout(scroll_content)
        grid.setSpacing(10)

        row, col = 0, 0
        for theme_id, display_name in themes_dict.items():
            btn = self.create_theme_card(theme_id, display_name)
            grid.addWidget(btn, row, col)
            self.theme_buttons[theme_id] = btn
            col += 1
            if col >= 2:
                col = 0
                row += 1

        scroll.setWidget(scroll_content)
        return scroll

    def switch_theme_mode(self, mode: str):
        self.current_theme_mode = mode
        if hasattr(self, "theme_stack"):
            self.theme_stack.setCurrentIndex(0 if mode == "day" else 1)
        self._update_mode_buttons_style()

    def _update_mode_buttons_style(self):
        if not hasattr(self, "btn_day_mode") or not hasattr(self, "btn_night_mode"):
            return
        pal = get_theme_palette(self.selected_theme)
        accent = pal.get("accent", "#d4a373")
        card_inset = pal.get("card_inset", "#2e2119")
        card_bg = pal.get("card_bg", "#241a13")
        border = pal.get("border", "#4a3729")
        fg = pal.get("fg", "#faecd0")
        is_day_active = (self.current_theme_mode == "day")

        style_active = f"""
            QPushButton {{
                background-color: {accent};
                color: #ffffff;
                font-weight: 800;
                font-size: 13px;
                border-radius: 8px;
                border: 2px solid {accent};
            }}
        """
        style_inactive = f"""
            QPushButton {{
                background-color: {card_inset};
                color: {fg};
                font-weight: 600;
                font-size: 13px;
                border-radius: 8px;
                border: 1px solid {border};
            }}
            QPushButton:hover {{
                border-color: {accent};
                background-color: {card_bg};
            }}
        """
        self.btn_day_mode.setStyleSheet(style_active if is_day_active else style_inactive)
        self.btn_night_mode.setStyleSheet(style_inactive if is_day_active else style_active)

    def create_theme_card(self, theme_id: str, display_name: str) -> QPushButton:
        pal = THEME_PALETTES.get(theme_id, THEME_PALETTES["coffee_mocha"])
        bg = pal.get("bg", "#1a120e")
        card = pal.get("card_bg", "#241a13")
        accent = pal.get("accent", "#d4a373")
        gold = pal.get("gold", "#f4c06b")

        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(54)
        btn.clicked.connect(lambda checked=False, t=theme_id: self.select_theme(t))

        card_layout = QHBoxLayout(btn)
        card_layout.setContentsMargins(12, 6, 12, 6)

        # Title
        lbl_name = QLabel(display_name)
        lbl_name.setStyleSheet("font-weight: 700; font-size: 13px; color: inherit;")
        card_layout.addWidget(lbl_name)
        card_layout.addStretch()

        # 4 Mini Color Dots
        dots_layout = QHBoxLayout()
        dots_layout.setSpacing(4)
        for c in (bg, card, accent, gold):
            dot = QLabel()
            dot.setFixedSize(14, 14)
            dot.setStyleSheet(f"background-color: {c}; border-radius: 7px; border: 1px solid rgba(255,255,255,0.25);")
            dots_layout.addWidget(dot)
        card_layout.addLayout(dots_layout)

        return btn

    def select_theme(self, theme_id: str):
        self.selected_theme = theme_id
        self._update_theme_cards_state()
        self.apply_dialog_theme(theme_id)

        # Apply live preview across Anki
        try:
            import sys
            mod = sys.modules.get(__package__) or sys.modules.get("AnkiBiotic")
            if mod and hasattr(mod, "apply_theme_quick"):
                mod.apply_theme_quick(theme_id)
            else:
                from . import apply_theme_quick
                apply_theme_quick(theme_id)
        except Exception:
            pass

    def _update_theme_cards_state(self):
        pal = get_theme_palette(self.selected_theme)
        accent = pal.get("accent", "#d4a373")
        border = pal.get("border", "#4a3729")

        for tid, btn in self.theme_buttons.items():
            if tid == self.selected_theme:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {pal.get('card_bg')};
                        border: 2px solid {accent};
                        border-radius: 8px;
                        color: {pal.get('fg')};
                        text-align: right;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {pal.get('card_inset')};
                        border: 1px solid {border};
                        border-radius: 8px;
                        color: {pal.get('fg')};
                        text-align: right;
                    }}
                    QPushButton:hover {{
                        border-color: {accent};
                    }}
                """)

    # ============================================================
    # TAB 2: PROFILE & AVATAR
    # ============================================================
    def create_profile_tab(self) -> QWidget:
        scroll_outer = QScrollArea()
        scroll_outer.setWidgetResizable(True)
        scroll_outer.setFrameShape(QFrame.Shape.NoFrame)
        scroll_outer.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        if scroll_outer.viewport():
            scroll_outer.viewport().setStyleSheet("background-color: transparent; background: transparent; border: none;")

        widget = QWidget()
        widget.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Compact User Info Box (Side-by-side) ──
        grp_info = QGroupBox("📝 بيانات المستخدم والشعار")
        h_info = QHBoxLayout(grp_info)
        h_info.setSpacing(14)
        h_info.setContentsMargins(12, 10, 12, 10)

        v_user = QVBoxLayout()
        v_user.setSpacing(4)
        lbl_u = QLabel("اسم المستخدم (Username):")
        lbl_u.setStyleSheet("font-size: 11px; font-weight: 700;")
        self.txt_username = QLineEdit()
        self.txt_username.setText(self.cfg.get("user_name", "المستخدم"))
        self.txt_username.setPlaceholderText("أدخل اسمك...")
        v_user.addWidget(lbl_u)
        v_user.addWidget(self.txt_username)
        h_info.addLayout(v_user)

        v_sub = QVBoxLayout()
        v_sub.setSpacing(4)
        lbl_s = QLabel("الوصف الفرعي أو الشعار (Subtitle):")
        lbl_s.setStyleSheet("font-size: 11px; font-weight: 700;")
        self.txt_subtitle = QLineEdit()
        self.txt_subtitle.setText(self.cfg.get("profile_subtitle", "طالب علم ومراجع متميز"))
        self.txt_subtitle.setPlaceholderText("وصف مختصر أو شعار تحفيزي...")
        v_sub.addWidget(lbl_s)
        v_sub.addWidget(self.txt_subtitle)
        h_info.addLayout(v_sub)

        layout.addWidget(grp_info, 0)

        # ── Avatar Presets & Custom Picture ──
        grp_avatar = QGroupBox("🖼️ اختيار الصورة الرمزية (Avatar)")
        vbox_av = QVBoxLayout(grp_avatar)
        vbox_av.setSpacing(10)
        vbox_av.setContentsMargins(12, 12, 12, 12)

        # Live Avatar Preview & Status Header
        preview_box = QHBoxLayout()
        preview_box.setSpacing(14)

        self.lbl_avatar_preview = QLabel()
        self.lbl_avatar_preview.setFixedSize(52, 52)
        self.lbl_avatar_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_box.addWidget(self.lbl_avatar_preview)

        status_vbox = QVBoxLayout()
        status_vbox.setSpacing(3)
        self.lbl_custom_path = QLabel()
        self.lbl_avatar_hint = QLabel("اختر شخصية رمزية جاهزة أو حدد صورة مخصصة من جهازك:")
        self.lbl_avatar_hint.setStyleSheet("font-size: 11px; opacity: 0.8;")
        status_vbox.addWidget(self.lbl_custom_path)
        status_vbox.addWidget(self.lbl_avatar_hint)
        preview_box.addLayout(status_vbox)
        preview_box.addStretch()

        vbox_av.addLayout(preview_box)

        # ── Category Filter Bar for Avatars ──
        cat_bar = QHBoxLayout()
        cat_bar.setSpacing(6)

        for cat_key, cat_title in AVATAR_CATEGORIES.items():
            btn_cat = QPushButton(cat_title)
            btn_cat.setFixedHeight(32)
            btn_cat.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_cat.clicked.connect(lambda checked=False, k=cat_key: self.filter_avatars(k))
            cat_bar.addWidget(btn_cat)
            self.avatar_category_buttons[cat_key] = btn_cat

        vbox_av.addLayout(cat_bar)

        # ── Preset Avatar Grid in Transparent Scroll Area ──
        self.scroll_av = QScrollArea()
        self.scroll_av.setWidgetResizable(True)
        self.scroll_av.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_av.setMinimumHeight(280)
        self.scroll_av.setFixedHeight(310)
        self.scroll_av.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        if self.scroll_av.viewport():
            self.scroll_av.viewport().setStyleSheet("background-color: transparent; background: transparent; border: none;")

        self.scroll_av_widget = QWidget()
        self.scroll_av_widget.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        self.av_grid = QGridLayout(self.scroll_av_widget)
        self.av_grid.setContentsMargins(0, 4, 8, 4)
        self.av_grid.setSpacing(8)

        def _make_avatar_handler(av_key: str):
            return lambda: self.select_avatar_preset(av_key)

        for av_id, av_info in AVATAR_PRESETS.items():
            btn_av = QPushButton(av_info["title"])
            btn_av.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_av.setFixedHeight(40)
            btn_av.clicked.connect(_make_avatar_handler(av_id))
            self.avatar_buttons[av_id] = btn_av

        self.rebuild_avatar_grid()
        self.scroll_av.setWidget(self.scroll_av_widget)
        vbox_av.addWidget(self.scroll_av, 1)
        layout.addWidget(grp_avatar, 1)

        # ── Dedicated Custom Image Group ──
        grp_custom = QGroupBox("📁 استخدام صورة مخصصة من جهازك (اختياري)")
        custom_layout = QVBoxLayout(grp_custom)
        custom_layout.setSpacing(8)
        custom_layout.setContentsMargins(12, 10, 12, 10)

        lbl_custom_desc = QLabel("يمكنك رفع أي صورة شخصية أو شعار من حاسوبك (PNG, JPG, SVG, WebP) لاستخدامه كرمز تعريفي:")
        lbl_custom_desc.setStyleSheet("font-size: 11px; opacity: 0.85;")
        custom_layout.addWidget(lbl_custom_desc)

        custom_box = QHBoxLayout()
        custom_box.setSpacing(10)

        btn_browse = QPushButton("📁 تصفح واختيار صورة...")
        btn_browse.setFixedHeight(34)
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self.browse_custom_avatar)
        custom_box.addWidget(btn_browse)

        self.btn_clear_avatar = QPushButton("🗑️ إزالة الصورة المخصصة")
        self.btn_clear_avatar.setFixedHeight(34)
        self.btn_clear_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_avatar.clicked.connect(self.clear_custom_avatar)
        custom_box.addWidget(self.btn_clear_avatar)
        custom_layout.addLayout(custom_box)

        layout.addWidget(grp_custom, 0)

        self._update_avatar_preview()
        self._update_custom_path_label()
        self._update_avatar_buttons_state()
        self._update_category_buttons_style()

        scroll_outer.setWidget(widget)
        return scroll_outer

    def filter_avatars(self, category_key: str):
        self.selected_avatar_category = category_key
        self.rebuild_avatar_grid()
        self._update_category_buttons_style()
        self._update_avatar_buttons_state()

    def rebuild_avatar_grid(self):
        while self.av_grid.count():
            item = self.av_grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        col, row = 0, 0
        for av_id, av_info in AVATAR_PRESETS.items():
            btn_cat = av_info.get("category", "academic")
            if self.selected_avatar_category != "all" and btn_cat != self.selected_avatar_category:
                continue

            btn = self.avatar_buttons[av_id]
            self.av_grid.addWidget(btn, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _update_category_buttons_style(self):
        pal = get_theme_palette(self.selected_theme)
        accent = pal.get("accent", "#d4a373")
        gold = pal.get("gold", "#f4c06b")
        card_bg = pal.get("card_bg", "#241a13")
        card_inset = pal.get("card_inset", "#2e2119")
        border = pal.get("border", "#4a3729")
        fg = pal.get("fg", "#faecd0")
        fg_muted = pal.get("fg_muted", "#b89f8c")

        for cat_k, cat_btn in self.avatar_category_buttons.items():
            if cat_k == self.selected_avatar_category:
                cat_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {accent};
                        color: {pal.get('bg', '#ffffff')};
                        border: 1px solid {gold};
                        border-radius: 6px;
                        font-weight: 800;
                        font-size: 11px;
                        padding: 4px 8px;
                    }}
                """)
            else:
                cat_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {card_inset};
                        color: {fg_muted};
                        border: 1px solid {border};
                        border-radius: 6px;
                        font-size: 11px;
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        color: {fg};
                        border-color: {accent};
                    }}
                """)

    def select_avatar_preset(self, av_id: str):
        self.selected_avatar = av_id
        self.custom_avatar_path = ""
        self._update_avatar_preview()
        self._update_custom_path_label()
        self._update_avatar_buttons_state()

    def browse_custom_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر صورة للملف الشخصي", "", "Images (*.png *.jpg *.jpeg *.svg *.webp)"
        )
        if file_path:
            self.custom_avatar_path = file_path
            self.selected_avatar = "custom"
            self._update_avatar_preview()
            self._update_custom_path_label()
            self._update_avatar_buttons_state()

    def clear_custom_avatar(self):
        self.custom_avatar_path = ""
        self.selected_avatar = "default"
        self._update_avatar_preview()
        self._update_custom_path_label()
        self._update_avatar_buttons_state()


    def _update_avatar_preview(self):
        if not hasattr(self, "lbl_avatar_preview"):
            return
        pal = get_theme_palette(self.selected_theme)
        gold = pal.get("gold", "#f4c06b")
        card_inset = pal.get("card_inset", "#2e2119")

        if self.custom_avatar_path and os.path.exists(self.custom_avatar_path):
            from aqt.qt import QPixmap
            pix = QPixmap(self.custom_avatar_path)
            if not pix.isNull():
                scaled = pix.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.lbl_avatar_preview.setPixmap(scaled)
                self.lbl_avatar_preview.setText("")
                self.lbl_avatar_preview.setStyleSheet(f"""
                    border: 2px solid {gold};
                    border-radius: 27px;
                    background-color: {card_inset};
                """)
                return

        # Preset emoji representation in preview
        emoji_map = {
            "default": "☕", "student": "🎓", "doctor": "🩺", "researcher": "🔬",
            "book": "📚", "engineer": "⚙️", "coder": "💻", "pharmacist": "💊",
            "dentist": "🦷", "lawyer": "⚖️", "mathematician": "📐", "linguist": "🗣️",
            "artist": "🎨", "writer": "✒️", "astronomer": "🔭", "neuro": "🧠",
            "champion": "🏆", "nature": "🌿", "historian": "🏛️", "pilot": "✈️"
        }
        em = emoji_map.get(self.selected_avatar)
        if not em:
            info = AVATAR_PRESETS.get(self.selected_avatar, {})
            title = info.get("title", "")
            em = title.split()[0] if title else "☕"

        self.lbl_avatar_preview.setText(em)
        self.lbl_avatar_preview.setStyleSheet(f"""
            border: 2px solid {gold};
            border-radius: 27px;
            background-color: {card_inset};
            font-size: 26px;
        """)


    def _update_custom_path_label(self):
        if not hasattr(self, "lbl_custom_path"):
            return
        pal = get_theme_palette(self.selected_theme)
        gold = pal.get("gold", "#f4c06b")

        if self.custom_avatar_path and os.path.exists(self.custom_avatar_path):
            name = os.path.basename(self.custom_avatar_path)
            self.lbl_custom_path.setText(f"✅ تم تحديد صورة مخصصة من الجهاز: {name}")
            self.lbl_custom_path.setStyleSheet("color: #4fa85b; font-weight: 800; font-size: 12px;")
        else:
            info = AVATAR_PRESETS.get(self.selected_avatar, AVATAR_PRESETS["default"])
            title = info.get("title", "☕ موكا أنكي (افتراضي)")
            self.lbl_custom_path.setText(f"✅ الشخصية الرمزية المحددة: {title}")
            self.lbl_custom_path.setStyleSheet(f"color: {gold}; font-weight: 800; font-size: 12px;")

    def _update_avatar_buttons_state(self):
        pal = get_theme_palette(self.selected_theme)
        accent = pal.get("accent", "#d4a373")
        gold = pal.get("gold", "#f4c06b")
        card_bg = pal.get("card_bg", "#241a13")
        card_inset = pal.get("card_inset", "#2e2119")
        border = pal.get("border", "#4a3729")
        fg = pal.get("fg", "#faecd0")

        for aid, btn in self.avatar_buttons.items():
            info = AVATAR_PRESETS.get(aid, {})
            base_title = info.get("title", aid)
            is_active = (aid == self.selected_avatar and not self.custom_avatar_path)

            if is_active:
                btn.setText(f"✔  {base_title}")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {card_bg};
                        border: 2px solid {gold};
                        border-radius: 8px;
                        font-weight: 800;
                        color: {gold};
                        font-size: 13px;
                        text-align: center;
                    }}
                """)
            else:
                btn.setText(base_title)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {card_inset};
                        border: 1px solid {border};
                        border-radius: 8px;
                        color: {fg};
                        font-size: 12px;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        border-color: {accent};
                        color: {gold};
                    }}
                """)

    # ============================================================
    # TAB 3: HEATMAP & STATS
    # ============================================================
    def create_heatmap_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(14, 14, 14, 14)

        # Heatmap Group
        grp_hm = QGroupBox("📊 خيارات خريطة النشاط والمراجعة (Heatmap)")
        form_hm = QFormLayout(grp_hm)
        form_hm.setSpacing(10)

        self.cmb_hm_default = QComboBox()
        self.cmb_hm_default.addItem("سنة كاملة (52 أسبوعاً)", "year")
        self.cmb_hm_default.addItem("شهر كامل", "month")
        self.cmb_hm_default.addItem("أسبوع واحد", "week")
        cur_def = self.cfg.get("default_heatmap_view", "year")
        idx_def = self.cmb_hm_default.findData(cur_def)
        if idx_def >= 0:
            self.cmb_hm_default.setCurrentIndex(idx_def)
        form_hm.addRow("العرض الافتراضي عند فتح التطبيق:", self.cmb_hm_default)

        self.cmb_start_week = QComboBox()
        self.cmb_start_week.addItem("الأحد (Sunday)", "sunday")
        self.cmb_start_week.addItem("السبت (Saturday)", "saturday")
        self.cmb_start_week.addItem("الاثنين (Monday)", "monday")
        cur_sw = self.cfg.get("start_of_week", "sunday")
        idx_sw = self.cmb_start_week.findData(cur_sw)
        if idx_sw >= 0:
            self.cmb_start_week.setCurrentIndex(idx_sw)
        form_hm.addRow("يوم بداية الأسبوع في الجدول:", self.cmb_start_week)

        self.chk_streak = QCheckBox("إظهار شارة السلسلة اليومية المتواصلة (🔥 Streak)")
        self.chk_streak.setChecked(bool(self.cfg.get("show_streak", True)))
        form_hm.addRow("", self.chk_streak)

        layout.addWidget(grp_hm)

        # Stats Cards Group
        grp_stats = QGroupBox("📈 بطاقات الإحصائيات المباشرة (Live Stats)")
        vbox_stats = QVBoxLayout(grp_stats)
        vbox_stats.setSpacing(8)

        lbl_stats_note = QLabel("حدد بطاقات الإحصائيات التي ترغب في إظهارها في لوحة التحكم:")
        lbl_stats_note.setStyleSheet("font-size: 11px;")
        vbox_stats.addWidget(lbl_stats_note)

        self.chk_stat_studied = QCheckBox("✅ بطاقة: البطاقات المراجعة اليوم (جديدة، تعلم، مستحقة)")
        self.chk_stat_studied.setChecked(bool(self.cfg.get("show_stat_studied", True)))
        vbox_stats.addWidget(self.chk_stat_studied)

        self.chk_stat_retention = QCheckBox("✅ بطاقة: معدل الاستبقاء ودقة الإجابات الصحيحة (%)")
        self.chk_stat_retention.setChecked(bool(self.cfg.get("show_stat_retention", True)))
        vbox_stats.addWidget(self.chk_stat_retention)

        self.chk_stat_pace = QCheckBox("✅ بطاقة: سرعة المراجعة (ثانية/بطاقة وبطاقة/ثانية)")
        self.chk_stat_pace.setChecked(bool(self.cfg.get("show_stat_pace", True)))
        vbox_stats.addWidget(self.chk_stat_pace)

        self.chk_stat_time = QCheckBox("✅ بطاقة: إجمالي وقت المراجعة المستغرق اليوم")
        self.chk_stat_time.setChecked(bool(self.cfg.get("show_stat_time", True)))
        vbox_stats.addWidget(self.chk_stat_time)

        layout.addWidget(grp_stats)
        layout.addStretch()
        return widget

    # ============================================================
    # TAB 4: LAYOUT & DECKS
    # ============================================================
    def create_layout_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(14, 14, 14, 14)

        # Decks Settings
        grp_decks = QGroupBox("🗂️ شجرة الرزم والفرز (Deck Hierarchy)")
        vbox_decks = QVBoxLayout(grp_decks)
        vbox_decks.setSpacing(8)

        self.chk_collapse_decks = QCheckBox("طي الرزم الفرعية افتراضياً عند فتح لوحة التحكم")
        self.chk_collapse_decks.setChecked(bool(self.cfg.get("decks_default_collapsed", False)))
        vbox_decks.addWidget(self.chk_collapse_decks)

        layout.addWidget(grp_decks)

        # Quick Navigation
        grp_nav = QGroupBox("⚡ شريط الوصول السريع (Quick Navigation)")
        vbox_nav = QVBoxLayout(grp_nav)
        vbox_nav.setSpacing(8)

        self.chk_quick_nav = QCheckBox("إظهار شريط الأزرار السريعة (إضافة، تصفح، إحصاء، مزامنة، إعدادات)")
        self.chk_quick_nav.setChecked(bool(self.cfg.get("show_quick_nav", True)))
        vbox_nav.addWidget(self.chk_quick_nav)

        layout.addWidget(grp_nav)

        # Information & Tips
        grp_info = QGroupBox("💡 تلميحات مفيدة")
        vbox_info = QVBoxLayout(grp_info)
        lbl_tip1 = QLabel("• يمكنك تغيير النمط فورياً في أي وقت دون فتح الإعدادات عبر القائمة العلوية ☕ AnkiBiotic.")
        lbl_tip2 = QLabel("• انقر على أي مربع في خريطة النشاط للبحث الفوري عن مراجعات ذلك اليوم.")
        lbl_tip3 = QLabel("• جميع الألوان والخطوط مصممة لتكون متوافقة مع جلسات المذاكرة الطويلة.")
        for l in (lbl_tip1, lbl_tip2, lbl_tip3):
            l.setStyleSheet("font-size: 11px; opacity: 0.85; padding: 2px 0;")
            vbox_info.addWidget(l)

        layout.addWidget(grp_info)
        layout.addStretch()
        return widget

    # ============================================================
    # TAB: GOALS, LANGUAGE & TYPOGRAPHY
    # ============================================================
    def create_general_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(14, 14, 14, 14)

        # 1. Language & Direction
        grp_lang = QGroupBox("🌐 لغة الواجهة والاتجاه (Language & Direction)")
        form_lang = QFormLayout(grp_lang)
        form_lang.setSpacing(10)

        self.cmb_language = QComboBox()
        self.cmb_language.addItem("العربية (Arabic - RTL)", "ar")
        self.cmb_language.addItem("English (English - LTR)", "en")
        cur_lang = self.cfg.get("language", "ar")
        idx_lang = self.cmb_language.findData(cur_lang)
        if idx_lang >= 0:
            self.cmb_language.setCurrentIndex(idx_lang)
        form_lang.addRow("اختر لغة العرض للوحة التحكم:", self.cmb_language)
        layout.addWidget(grp_lang)

        # 2. Daily Study Goal & ETA
        grp_goal = QGroupBox("🎯 هدف الدراسة اليومي وحاسبة الوقت (Daily Goal & ETA)")
        form_goal = QFormLayout(grp_goal)
        form_goal.setSpacing(10)

        self.chk_goal_enabled = QCheckBox("تفعيل هدف الدراسة اليومي وشريط التقدم (Daily Goal Progress Bar)")
        self.chk_goal_enabled.setChecked(bool(self.cfg.get("daily_goal_enabled", True)))
        form_goal.addRow("", self.chk_goal_enabled)

        self.spn_goal_cards = QSpinBox()
        self.spn_goal_cards.setRange(5, 5000)
        self.spn_goal_cards.setSingleStep(10)
        self.spn_goal_cards.setValue(int(self.cfg.get("daily_goal_cards", 100)))
        form_goal.addRow("عدد البطاقات المستهدفة يومياً (بطاقة):", self.spn_goal_cards)

        self.chk_show_eta = QCheckBox("إظهار حاسبة وقت الانتهاء المتوقع اليومي (Estimated Finish Time / ETA)")
        self.chk_show_eta.setChecked(bool(self.cfg.get("show_eta", True)))
        form_goal.addRow("", self.chk_show_eta)

        layout.addWidget(grp_goal)

        # 3. Typography & UI Zoom Scaling
        grp_font = QGroupBox("🔤 تخصيص الخطوط وحجم الواجهة (Fonts & UI Scaling)")
        form_font = QFormLayout(grp_font)
        form_font.setSpacing(10)

        self.cmb_font_family = QComboBox()
        for f_key, f_val in get_available_fonts().items():
            self.cmb_font_family.addItem(f_val["name"], f_key)
        cur_font = self.cfg.get("font_family_preset", "cairo")
        idx_font = self.cmb_font_family.findData(cur_font)
        if idx_font >= 0:
            self.cmb_font_family.setCurrentIndex(idx_font)
        form_font.addRow("نوع الخط المستخدم في الواجهة:", self.cmb_font_family)

        self.cmb_ui_scale = QComboBox()
        self.cmb_ui_scale.addItem("90% (مدمج وصغير)", 90)
        self.cmb_ui_scale.addItem("100% (الافتراضي)", 100)
        self.cmb_ui_scale.addItem("110% (متوسط وكبير)", 110)
        self.cmb_ui_scale.addItem("120% (كبير جداً)", 120)
        cur_scale = int(self.cfg.get("ui_scale", 100))
        idx_scale = self.cmb_ui_scale.findData(cur_scale)
        if idx_scale >= 0:
            self.cmb_ui_scale.setCurrentIndex(idx_scale)
        form_font.addRow("مقياس تكبير الواجهة (Zoom Scaling):", self.cmb_ui_scale)

        layout.addWidget(grp_font)
        layout.addStretch()
        return widget

    # ============================================================
    # TAB: ACHIEVEMENTS & BADGES
    # ============================================================
    def create_badges_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(14, 14, 14, 14)

        lbl_info = QLabel("استعرض الشارات والإنجازات التي حققتها بناءً على استمراريتك ومعدل مراجعاتك:")
        lbl_info.setStyleSheet("font-size: 12px; font-weight: 700;")
        layout.addWidget(lbl_info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        if scroll.viewport():
            scroll.viewport().setStyleSheet("background-color: transparent; background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent; background: transparent; border: none;")
        grid = QGridLayout(scroll_content)
        grid.setSpacing(10)

        # Compute badges live
        stats = get_stats_data(lang=self.cfg.get("language", "ar"))
        hm_data = get_ankibiotic_heatmap_data()
        badges = compute_badges(stats, total_reviews_ever=hm_data.get("total_reviews", 0), lang=self.cfg.get("language", "ar"))

        pal = get_theme_palette(self.selected_theme)
        card_bg = pal.get("card_bg", "#241a13")
        card_inset = pal.get("card_inset", "#2e2119")
        border = pal.get("border", "#4a3729")
        gold = pal.get("gold", "#f4c06b")
        fg = pal.get("fg", "#faecd0")
        fg_muted = pal.get("fg_muted", "#a89080")

        for idx, b in enumerate(badges):
            b_box = QFrame()
            b_box.setFrameShape(QFrame.Shape.StyledPanel)
            is_unlocked = b["unlocked"]
            border_color = gold if is_unlocked else border
            bg_color = card_bg if is_unlocked else card_inset

            b_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                    padding: 10px;
                }}
            """)

            if not is_unlocked:
                try:
                    from aqt.qt import QGraphicsOpacityEffect
                    op_effect = QGraphicsOpacityEffect(b_box)
                    op_effect.setOpacity(0.55)
                    b_box.setGraphicsEffect(op_effect)
                except Exception:
                    pass

            b_layout = QVBoxLayout(b_box)
            b_layout.setSpacing(4)

            top_row = QHBoxLayout()
            lbl_icon = QLabel(b["icon"])
            lbl_icon.setStyleSheet("font-size: 22px;")
            top_row.addWidget(lbl_icon)

            status_text = "✅ محقق" if is_unlocked else "🔒 قيد الإنجاز"
            status_color = "#5b8e55" if is_unlocked else fg_muted
            lbl_status = QLabel(status_text)
            lbl_status.setStyleSheet(f"font-size: 10px; font-weight: 800; color: {status_color};")
            top_row.addStretch()
            top_row.addWidget(lbl_status)
            b_layout.addLayout(top_row)

            lbl_title = QLabel(b["title"])
            lbl_title.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {gold if is_unlocked else fg};")
            b_layout.addWidget(lbl_title)

            lbl_desc = QLabel(b["desc"])
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet(f"font-size: 10px; color: {fg_muted};")
            b_layout.addWidget(lbl_desc)

            lbl_prog = QLabel(f"التقدم: {b['progress_str']}")
            lbl_prog.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {fg}; margin-top: 4px;")
            b_layout.addWidget(lbl_prog)

            row = idx // 2
            col = idx % 2
            grid.addWidget(b_box, row, col)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return widget

    # ============================================================
    # THEME STYLING
    # ============================================================

    def apply_dialog_theme(self, theme_id: str):
        """Styles the dialog and all its tabs to match the chosen theme palette."""
        pal = get_theme_palette(theme_id)
        bg = pal["bg"]
        card_bg = pal["card_bg"]
        card_inset = pal["card_inset"]
        border = pal["border"]
        fg = pal["fg"]
        fg_muted = pal["fg_muted"]
        accent = pal["accent"]
        accent_hover = pal["accent_hover"]
        gold = pal["gold"]

        qss = f"""
            QDialog {{
                background-color: {bg};
                color: {fg};
                font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
            }}
            QScrollArea, QScrollArea > QWidget, QAbstractScrollArea, QAbstractScrollArea::viewport {{
                background-color: transparent;
                background: transparent;
                border: none;
            }}
            QLabel {{
                color: {fg};
            }}
            QTabWidget::pane {{
                border: 1px solid {border};
                border-radius: 12px;
                background-color: {card_bg};
                padding: 6px;
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: {card_inset};
                color: {fg_muted};
                border: 1px solid {border};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 18px;
                font-weight: 700;
                font-size: 12px;
                margin-left: 3px;
            }}
            QTabBar::tab:selected {{
                background-color: {card_bg};
                color: {gold};
                border-bottom: 2px solid {accent};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {card_bg};
                color: {fg};
            }}
            QGroupBox {{
                background-color: {card_bg};
                border: 1px solid {border};
                border-radius: 10px;
                margin-top: 14px;
                padding-top: 16px;
                font-weight: bold;
                color: {gold};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 8px;
                color: {gold};
            }}
            QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
                background-color: {card_inset};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 6px 10px;
                color: {fg};
                font-size: 13px;
                selection-background-color: {accent};
            }}
            QComboBox QAbstractItemView {{
                background-color: {card_bg};
                border: 1px solid {border};
                selection-background-color: {accent};
                color: {fg};
            }}
            QCheckBox {{
                color: {fg};
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {border};
                background-color: {card_inset};
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent};
                border-color: {accent};
            }}
            QPushButton {{
                background-color: {card_inset};
                color: {fg};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 7px 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                border-color: {accent};
                color: {gold};
            }}
            QPushButton#btn_save {{
                background-color: {accent};
                color: {bg};
                border: none;
                font-weight: 800;
                font-size: 13px;
            }}
            QPushButton#btn_save:hover {{
                background-color: {accent_hover};
            }}
            QPushButton#btn_reset {{
                background-color: transparent;
                border: 1px solid #732d2d;
                color: #e06666;
            }}
            QPushButton#btn_reset:hover {{
                background-color: #4a1e1e;
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {card_inset};
                width: 6px;
                border-radius: 3px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border};
                border-radius: 3px;
                min-height: 25px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {accent};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        self.setStyleSheet(qss)
        self._update_theme_cards_state()
        self._update_avatar_buttons_state()
        self._update_mode_buttons_style()
        self._update_category_buttons_style()
        self._update_avatar_preview()
        self._update_custom_path_label()
        if hasattr(self, "scroll_av") and self.scroll_av:
            self.scroll_av.setStyleSheet("background-color: transparent; background: transparent; border: none;")
            if self.scroll_av.viewport():
                self.scroll_av.viewport().setStyleSheet("background-color: transparent; background: transparent; border: none;")

    # ============================================================
    # SAVE & RESET
    # ============================================================
    def reset_defaults(self):
        """Reset configuration to defaults."""
        reply = QMessageBox.question(
            self,
            "إعادة الضبط الافتراضي",
            "هل أنت متأكد من إعادة جميع الإعدادات للقيم الافتراضية الأصلية؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            reset_config()
            self.accept()
            if mw and hasattr(mw, "deckBrowser") and mw.deckBrowser:
                mw.deckBrowser.refresh()

    def save(self):
        invalidate_cache()
        self.cfg = load_config()

        # Themes & Appearance
        self.cfg["theme"] = self.selected_theme
        self.cfg["card_radius"] = self.spn_radius.value()
        self.cfg["card_opacity"] = self.spn_opacity.value()

        # Goals, Language & Typography
        self.cfg["language"] = self.cmb_language.currentData() or "ar"
        self.cfg["daily_goal_enabled"] = self.chk_goal_enabled.isChecked()
        self.cfg["daily_goal_cards"] = self.spn_goal_cards.value()
        self.cfg["show_eta"] = self.chk_show_eta.isChecked()
        self.cfg["font_family_preset"] = self.cmb_font_family.currentData() or "cairo"
        self.cfg["ui_scale"] = int(self.cmb_ui_scale.currentData() or 100)

        # Profile
        self.cfg["user_name"] = self.txt_username.text().strip() or "المستخدم"
        self.cfg["profile_subtitle"] = self.txt_subtitle.text().strip() or ""
        self.cfg["avatar_type"] = self.selected_avatar
        self.cfg["custom_avatar_path"] = self.custom_avatar_path


        # Heatmap & Stats
        self.cfg["default_heatmap_view"] = self.cmb_hm_default.currentData() or "year"
        self.cfg["start_of_week"] = self.cmb_start_week.currentData() or "sunday"
        self.cfg["show_streak"] = self.chk_streak.isChecked()
        self.cfg["show_stat_studied"] = self.chk_stat_studied.isChecked()
        self.cfg["show_stat_retention"] = self.chk_stat_retention.isChecked()
        self.cfg["show_stat_pace"] = self.chk_stat_pace.isChecked()
        self.cfg["show_stat_time"] = self.chk_stat_time.isChecked()

        # Layout & Decks
        self.cfg["decks_default_collapsed"] = self.chk_collapse_decks.isChecked()
        self.cfg["show_quick_nav"] = self.chk_quick_nav.isChecked()

        save_config(self.cfg)
        self.accept()

        # Refresh DeckBrowser to immediately show changes
        if mw and hasattr(mw, "deckBrowser") and mw.deckBrowser:
            mw.deckBrowser.refresh()


def open_settings_dialog():
    dlg = AnkiBioticSettingsDialog(mw)
    dlg.exec()
