"""
AnkiBiotic - Configuration & State Management
Multiple themes, dynamic settings, and persistent options.
"""

import os
import json
from typing import Any, Dict

# Day / Light Mode Themes (☀️ الوضع النهاري)
LIGHT_THEMES = {
    "light": "☀️ ناصع كلاسيكي",
    "arctic_frost": "❄️ صقيع قطبي",
    "latte_cream": "🥛 لاتيه كريمي",
    "mint_meadow": "🌿 نعناع هادئ",
    "lavender_mist": "🪻 رذاذ اللافندر",
    "rose_petal": "🌸 بتلات الورد",
    "desert_sand": "🏜️ رمال صحراوية",
    "nordic_slate": "📖 ورق اسكندنافي",
    "surgical_blue": "🏥 أزرق جراحي (Surgical)",
    "scrub_green": "🩺 أخضر السكرابز (Scrubs)",
    "citrus_dawn": "🍊 إشراقة الصباح (Citrus Dawn)",
    "matcha_tea": "🍵 ماتشا هادئة (Matcha Serenity)",
    "golden_parchment": "📜 مخطوطة أندلسية (Parchment)",
    "ocean_breeze": "⛵ نسيم البحر (Ocean Breeze)",
    "lilac_blossom": "🪻 ليلك ناعم (Lilac Blossom)",
    "stethoscope_teal": "🩺 تركواز سريري (Clinical Teal)",
}

# Night / Dark Mode Themes (🌙 الوضع الليلي)
DARK_THEMES = {
    "coffee_mocha": "☕ قهوة موكا",
    "dark": "🌙 داكن كلاسيكي",
    "ocean_deep": "🌊 أعماق المحيط",
    "forest_green": "🌲 غابة خضراء",
    "royal_purple": "👑 أرجواني ملكي",
    "midnight_blue": "🌃 أزرق منتصف الليل",
    "sunset_rose": "🌅 غروب مخملي",
    "cherry_blossom": "🌸 ساكورا ليلية",
    "cyber_emerald": "⚡ زمردي سايبر",
    "sandstorm": "🏜️ عاصفة رملية",
    "ecg_pulse": "🫀 نبضات القلب (ECG Pulse)",
    "oled_black": "🖤 سواد تام (OLED True Black)",
    "crimson_velvet": "🍷 مخمل ياقوتي (Crimson Velvet)",
    "dracula_vamp": "🧛 دراكولا القوطي (Dracula Night)",
    "amber_glow": "🕯️ توهج العنبر (Warm Amber)",
    "nebula_cosmic": "🌌 سديم كوني (Cosmic Nebula)",
    "synthwave_neon": "🌆 سينثويف نيون (Synthwave 80s)",
}

# Combined dictionary for backward compatibility
THEMES = {**LIGHT_THEMES, **DARK_THEMES}

THEME_PALETTES: Dict[str, Dict[str, str]] = {
    # ── Day Modes (☀️ الوضع النهاري) ──
    "light": {
        "bg": "#f5ede4", "card_bg": "#ffffff", "card_inset": "#f0e6d6",
        "border": "#d8c4a8", "fg": "#2d1e12", "fg_muted": "#7a5c40",
        "accent": "#9b6b3a", "accent_hover": "#b8834c", "gold": "#c07828"
    },
    "arctic_frost": {
        "bg": "#edf4fa", "card_bg": "#ffffff", "card_inset": "#e4edf6",
        "border": "#c0d4e6", "fg": "#14283e", "fg_muted": "#5a7490",
        "accent": "#2880c8", "accent_hover": "#4098e0", "gold": "#2070b0"
    },
    "latte_cream": {
        "bg": "#faf5ee", "card_bg": "#ffffff", "card_inset": "#f3ebdf",
        "border": "#dfd2c0", "fg": "#362618", "fg_muted": "#826b58",
        "accent": "#a06c3f", "accent_hover": "#bc8454", "gold": "#c68234"
    },
    "mint_meadow": {
        "bg": "#eef6f1", "card_bg": "#ffffff", "card_inset": "#e2efe6",
        "border": "#bcd8c6", "fg": "#163324", "fg_muted": "#4e7760",
        "accent": "#2d8a5e", "accent_hover": "#3ca874", "gold": "#309865"
    },
    "lavender_mist": {
        "bg": "#f4f1fa", "card_bg": "#ffffff", "card_inset": "#eae4f4",
        "border": "#cfc3e6", "fg": "#261b38", "fg_muted": "#6b5686",
        "accent": "#764db8", "accent_hover": "#9066d4", "gold": "#8250c6"
    },
    "rose_petal": {
        "bg": "#faf0f2", "card_bg": "#ffffff", "card_inset": "#f4e2e6",
        "border": "#e4bfc8", "fg": "#3a1922", "fg_muted": "#885060",
        "accent": "#c84666", "accent_hover": "#dc5c7c", "gold": "#d04e70"
    },
    "desert_sand": {
        "bg": "#f7f2ea", "card_bg": "#ffffff", "card_inset": "#ede4d4",
        "border": "#d6c3a6", "fg": "#342614", "fg_muted": "#806846",
        "accent": "#b87c32", "accent_hover": "#d29244", "gold": "#be7826"
    },
    "nordic_slate": {
        "bg": "#f0f3f6", "card_bg": "#ffffff", "card_inset": "#e4eaef",
        "border": "#c4d1dc", "fg": "#1a2530", "fg_muted": "#54687a",
        "accent": "#3a6890", "accent_hover": "#4e7ea8", "gold": "#35668e"
    },
    "surgical_blue": {
        "bg": "#eef5fa", "card_bg": "#ffffff", "card_inset": "#e1edf6",
        "border": "#b6cfdf", "fg": "#102a3d", "fg_muted": "#4d6c82",
        "accent": "#0f82b8", "accent_hover": "#179fdc", "gold": "#0284c7"
    },
    "scrub_green": {
        "bg": "#edf6f3", "card_bg": "#ffffff", "card_inset": "#dff0ea",
        "border": "#b0d8c8", "fg": "#123326", "fg_muted": "#467360",
        "accent": "#189a6c", "accent_hover": "#22b580", "gold": "#10b981"
    },
    "citrus_dawn": {
        "bg": "#fdf6ed", "card_bg": "#ffffff", "card_inset": "#faebda",
        "border": "#f0ceaa", "fg": "#381e08", "fg_muted": "#8a5a2e",
        "accent": "#e06d10", "accent_hover": "#f58226", "gold": "#f59e0b"
    },
    "matcha_tea": {
        "bg": "#f2f6ee", "card_bg": "#ffffff", "card_inset": "#e6eee0",
        "border": "#c6d8bc", "fg": "#1b3014", "fg_muted": "#526e48",
        "accent": "#4a7c36", "accent_hover": "#5f9c47", "gold": "#84cc16"
    },
    "golden_parchment": {
        "bg": "#faf4e8", "card_bg": "#fffdf9", "card_inset": "#f2e8d3",
        "border": "#d8c59e", "fg": "#342814", "fg_muted": "#7d6844",
        "accent": "#b3822a", "accent_hover": "#cfa043", "gold": "#d97706"
    },
    "ocean_breeze": {
        "bg": "#edf7f9", "card_bg": "#ffffff", "card_inset": "#ddf0f4",
        "border": "#b2dde6", "fg": "#0d2c33", "fg_muted": "#46747e",
        "accent": "#0891b2", "accent_hover": "#06b6d4", "gold": "#0284c7"
    },
    "lilac_blossom": {
        "bg": "#f8f4fb", "card_bg": "#ffffff", "card_inset": "#f0e6f6",
        "border": "#d9c0e6", "fg": "#2e1438", "fg_muted": "#70487d",
        "accent": "#9333ea", "accent_hover": "#a855f7", "gold": "#c084fc"
    },
    "stethoscope_teal": {
        "bg": "#ecfdf5", "card_bg": "#ffffff", "card_inset": "#d1fae5",
        "border": "#a7f3d0", "fg": "#064e3b", "fg_muted": "#047857",
        "accent": "#059669", "accent_hover": "#10b981", "gold": "#14b8a6"
    },

    # ── Night Modes (🌙 الوضع الليلي) ──
    "coffee_mocha": {
        "bg": "#1a120e", "card_bg": "#241a13", "card_inset": "#2e2119",
        "border": "#4a3729", "fg": "#faecd0", "fg_muted": "#b89f8c",
        "accent": "#d4a373", "accent_hover": "#e6be94", "gold": "#f4c06b"
    },
    "dark": {
        "bg": "#0e0e10", "card_bg": "#18181c", "card_inset": "#222228",
        "border": "#383840", "fg": "#eaeaf0", "fg_muted": "#8888a0",
        "accent": "#7c9cdc", "accent_hover": "#9ab5e8", "gold": "#f0d060"
    },
    "ocean_deep": {
        "bg": "#0a141e", "card_bg": "#0f1e2e", "card_inset": "#152838",
        "border": "#1e3c58", "fg": "#d8ecf8", "fg_muted": "#7a9ab8",
        "accent": "#38a8d8", "accent_hover": "#60c0e8", "gold": "#50c8e8"
    },
    "forest_green": {
        "bg": "#0e1a10", "card_bg": "#142018", "card_inset": "#1c2e1e",
        "border": "#2e4830", "fg": "#d8f0d0", "fg_muted": "#80a880",
        "accent": "#58b868", "accent_hover": "#70d080", "gold": "#b8d830"
    },
    "royal_purple": {
        "bg": "#12101a", "card_bg": "#1a1628", "card_inset": "#221e32",
        "border": "#3a3450", "fg": "#e8e0f8", "fg_muted": "#9088b0",
        "accent": "#a078e0", "accent_hover": "#b898f0", "gold": "#e0b050"
    },
    "midnight_blue": {
        "bg": "#0a0e18", "card_bg": "#101828", "card_inset": "#182038",
        "border": "#283860", "fg": "#d0e0f8", "fg_muted": "#6888b0",
        "accent": "#4888d8", "accent_hover": "#68a8f0", "gold": "#f8d050"
    },
    "sunset_rose": {
        "bg": "#1c100e", "card_bg": "#261416", "card_inset": "#321c1e",
        "border": "#502e30", "fg": "#f8e0d8", "fg_muted": "#b88888",
        "accent": "#e86878", "accent_hover": "#f08898", "gold": "#f8a860"
    },
    "cherry_blossom": {
        "bg": "#1a0e14", "card_bg": "#221420", "card_inset": "#2e1c2a",
        "border": "#4a3048", "fg": "#f4dce8", "fg_muted": "#a880a0",
        "accent": "#e070a0", "accent_hover": "#f090b8", "gold": "#f0a8c0"
    },
    "cyber_emerald": {
        "bg": "#0c1210", "card_bg": "#121b18", "card_inset": "#182622",
        "border": "#243c34", "fg": "#e0faed", "fg_muted": "#78aa96",
        "accent": "#00d68f", "accent_hover": "#26e8a4", "gold": "#38e0a0"
    },
    "sandstorm": {
        "bg": "#1e1810", "card_bg": "#282014", "card_inset": "#34281a",
        "border": "#504028", "fg": "#f0e0c0", "fg_muted": "#a89070",
        "accent": "#d8a850", "accent_hover": "#e8c070", "gold": "#f0c848"
    },
    "ecg_pulse": {
        "bg": "#080b0e", "card_bg": "#0e1419", "card_inset": "#141d24",
        "border": "#223340", "fg": "#e6f4f8", "fg_muted": "#6b8f9e",
        "accent": "#00e5a3", "accent_hover": "#2bffa8", "gold": "#ff4d6d"
    },
    "oled_black": {
        "bg": "#000000", "card_bg": "#0a0a0a", "card_inset": "#141414",
        "border": "#262626", "fg": "#ffffff", "fg_muted": "#888888",
        "accent": "#00e5ff", "accent_hover": "#33ebff", "gold": "#ffd600"
    },
    "crimson_velvet": {
        "bg": "#14080a", "card_bg": "#1c0d10", "card_inset": "#281418",
        "border": "#481e26", "fg": "#fae8ea", "fg_muted": "#ba848b",
        "accent": "#e11d48", "accent_hover": "#f43f5e", "gold": "#fbbf24"
    },
    "dracula_vamp": {
        "bg": "#1e1f29", "card_bg": "#282a36", "card_inset": "#343746",
        "border": "#44475a", "fg": "#f8f8f2", "fg_muted": "#a0a4bd",
        "accent": "#ff79c6", "accent_hover": "#ff92d0", "gold": "#bd93f9"
    },
    "amber_glow": {
        "bg": "#120e0a", "card_bg": "#1a140e", "card_inset": "#251c14",
        "border": "#423222", "fg": "#fef3c7", "fg_muted": "#bba078",
        "accent": "#f59e0b", "accent_hover": "#fbbf24", "gold": "#fbbf24"
    },
    "nebula_cosmic": {
        "bg": "#0c071e", "card_bg": "#130c2c", "card_inset": "#1c123d",
        "border": "#35236b", "fg": "#f3e8ff", "fg_muted": "#9d85c7",
        "accent": "#8b5cf6", "accent_hover": "#a78bfa", "gold": "#c084fc"
    },
    "synthwave_neon": {
        "bg": "#0d0818", "card_bg": "#160e28", "card_inset": "#22163b",
        "border": "#422068", "fg": "#fdf2f8", "fg_muted": "#b588c8",
        "accent": "#f43f5e", "accent_hover": "#fb7185", "gold": "#06b6d4"
    },
}

# Avatar categories and presets for profile personalization
AVATAR_CATEGORIES: Dict[str, str] = {
    "all": "🌟 الكل (28)",
    "academic": "🎓 أكاديمي وبحثي",
    "medical": "🩺 طبي وصحي",
    "tech": "💻 تقني وهندسي",
    "humanities": "🎨 أدبي وإبداعي",
}

def get_avatar_categories() -> Dict[str, str]:
    return dict(AVATAR_CATEGORIES)

AVATAR_PRESETS: Dict[str, Dict[str, str]] = {
    "default": {
        "title": "☕ موكا أنكي (افتراضي)",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <circle cx="50" cy="38" r="16" fill="var(--ab-gold)"/>
            <path d="M26 78C26 64.7452 36.7452 54 50 54C63.2548 54 74 64.7452 74 78V84H26V78Z" fill="var(--ab-accent)"/>
        </svg>"""
    },
    "student": {
        "title": "🎓 طالب علم متفوق",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 24L20 38L50 52L80 38L50 24Z" fill="var(--ab-gold)"/>
            <path d="M30 46V64C30 72 40 78 50 78C60 78 70 72 70 64V46" stroke="var(--ab-accent)" stroke-width="4" stroke-linecap="round" fill="none"/>
            <path d="M78 40V68" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round"/>
            <circle cx="78" cy="70" r="3" fill="var(--ab-gold)"/>
        </svg>"""
    },
    "doctor": {
        "title": "🩺 طبيب وممارس صحي",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <circle cx="50" cy="34" r="14" fill="var(--ab-gold)"/>
            <path d="M28 80C28 66 38 56 50 56C62 56 72 66 72 80" fill="var(--ab-accent)"/>
            <path d="M40 58C40 68 46 72 50 72C54 72 60 68 60 58" stroke="var(--ab-gold)" stroke-width="3" fill="none" stroke-linecap="round"/>
            <circle cx="50" cy="74" r="4" fill="var(--ab-gold)"/>
        </svg>"""
    },
    "med_student": {
        "title": "🩺 طالب طب وجراحة",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 16L24 28L50 40L76 28L50 16Z" fill="var(--ab-gold)"/>
            <path d="M34 34V48C34 53 41 57 50 57C59 57 66 53 66 48V34" stroke="var(--ab-gold)" stroke-width="2.5" fill="none"/>
            <path d="M74 30V52" stroke="var(--ab-accent)" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="74" cy="54" r="3" fill="var(--ab-accent)"/>
            <circle cx="50" cy="42" r="11" fill="var(--ab-accent)"/>
            <path d="M26 82C26 66 36 57 50 57C64 57 74 66 74 82V84H26V82Z" fill="var(--ab-card-inset)" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <path d="M38 58L50 72L62 58" stroke="var(--ab-gold)" stroke-width="2.5" fill="none"/>
            <path d="M37 60C37 72 44 76 50 76C56 72 63 60 63 60" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M50 76V80" stroke="var(--ab-gold)" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="50" cy="82" r="4" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="2"/>
            <path d="M30 68H36M33 65V71" stroke="var(--ab-gold)" stroke-width="2" stroke-linecap="round"/>
        </svg>"""
    },
    "caduceus_student": {
        "title": "⚕️ رمز الطب والمعرفة",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M24 64C34 60 44 62 50 66C56 62 66 60 76 64V80C66 76 56 78 50 82C44 78 34 76 24 80V64Z" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <path d="M50 66V82" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <path d="M50 20V66" stroke="var(--ab-gold)" stroke-width="4" stroke-linecap="round"/>
            <circle cx="50" cy="20" r="4" fill="var(--ab-gold)"/>
            <path d="M42 54C42 48 58 48 58 42C58 36 42 36 42 30C42 24 54 22 56 26" stroke="var(--ab-accent)" stroke-width="3.5" fill="none" stroke-linecap="round"/>
            <circle cx="57" cy="26" r="2.5" fill="var(--ab-gold)"/>
            <path d="M28 44C28 32 36 24 46 22M72 44C72 32 64 24 54 22" stroke="var(--ab-gold)" stroke-width="2" stroke-dasharray="3 3" fill="none"/>
        </svg>"""
    },
    "researcher": {
        "title": "🔬 باحث ومفكر علمي",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M44 24H56V38L68 64C72 72 66 80 56 80H44C34 80 28 72 32 64L44 38V24Z" stroke="var(--ab-gold)" stroke-width="4" fill="var(--ab-card-inset)"/>
            <path d="M38 58H62" stroke="var(--ab-accent)" stroke-width="3"/>
            <circle cx="50" cy="68" r="4" fill="var(--ab-accent)"/>
            <circle cx="44" cy="64" r="2.5" fill="var(--ab-gold)"/>
        </svg>"""
    },
    "book": {
        "title": "📚 قارئ وباحث معرفة",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M26 36C34 32 44 34 50 38C56 34 66 32 74 36V70C66 66 56 68 50 72C44 68 34 66 26 70V36Z" fill="var(--ab-accent)"/>
            <path d="M50 38V72" stroke="var(--ab-gold)" stroke-width="3"/>
            <path d="M30 42C36 39 44 40 48 43" stroke="var(--ab-card-inset)" stroke-width="2" stroke-linecap="round"/>
            <path d="M30 50C36 47 44 48 48 51" stroke="var(--ab-card-inset)" stroke-width="2" stroke-linecap="round"/>
            <path d="M70 42C64 39 56 40 52 43" stroke="var(--ab-card-inset)" stroke-width="2" stroke-linecap="round"/>
        </svg>"""
    },
    "engineer": {
        "title": "⚙️ مهندس ومبتكر تقني",
        "category": "tech",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <circle cx="50" cy="50" r="14" stroke="var(--ab-gold)" stroke-width="4" fill="none"/>
            <path d="M46 22H54V28H46V22ZM46 72H54V78H46V72ZM22 46H28V54H22V46ZM72 46H78V54H72V46ZM30 30L36 36L30 42L24 36L30 30ZM64 64L70 70L64 76L58 70L64 64ZM70 30L64 36L70 42L76 36L70 30ZM30 70L36 64L42 70L36 76L30 70Z" fill="var(--ab-accent)"/>
            <circle cx="50" cy="50" r="6" fill="var(--ab-gold)"/>
        </svg>"""
    },
    "coder": {
        "title": "💻 مبرمج ومطور أنظمة",
        "category": "tech",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <rect x="22" y="28" width="56" height="40" rx="6" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M34 44L28 48L34 52" stroke="var(--ab-accent)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M66 44L72 48L66 52" stroke="var(--ab-accent)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M53 42L47 54" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round"/>
            <path d="M36 74H64" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round"/>
        </svg>"""
    },
    "pharmacist": {
        "title": "💊 صيدلي وخبير دواء",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <rect x="44" y="24" width="12" height="26" rx="6" fill="var(--ab-accent)"/>
            <rect x="44" y="50" width="12" height="26" rx="6" fill="var(--ab-gold)"/>
            <circle cx="50" cy="50" r="28" stroke="var(--ab-gold)" stroke-width="2.5" stroke-dasharray="4 4" fill="none"/>
            <path d="M34 50H66M50 34V66" stroke="var(--ab-card-inset)" stroke-width="3.5" stroke-linecap="round"/>
        </svg>"""
    },
    "dentist": {
        "title": "🦷 طبيب وجراح أسنان",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M32 34C32 26 40 24 50 28C60 24 68 26 68 34C68 46 64 56 62 76C60 78 56 78 54 70L50 56L46 70C44 78 40 78 38 76C36 56 32 46 32 34Z" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="3"/>
            <path d="M68 28L72 32M72 28L68 32" stroke="var(--ab-gold)" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="70" cy="30" r="2" fill="var(--ab-gold)"/>
        </svg>"""
    },
    "lawyer": {
        "title": "⚖️ حقوقي ومستشار قانوني",
        "category": "humanities",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 22V76M36 76H64" stroke="var(--ab-gold)" stroke-width="3.5" stroke-linecap="round"/>
            <path d="M26 34H74" stroke="var(--ab-gold)" stroke-width="3.5" stroke-linecap="round"/>
            <path d="M26 34L20 54H40L34 34" stroke="var(--ab-accent)" stroke-width="2.5" fill="none"/>
            <path d="M20 54C20 60 40 60 40 54Z" fill="var(--ab-accent)"/>
            <path d="M66 34L60 54H80L74 34" stroke="var(--ab-accent)" stroke-width="2.5" fill="none"/>
            <path d="M60 54C60 60 80 60 80 54Z" fill="var(--ab-accent)"/>
        </svg>"""
    },
    "mathematician": {
        "title": "📐 عالم رياضيات وفيزياء",
        "category": "tech",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M30 30H70L50 50L70 70H30" stroke="var(--ab-gold)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <circle cx="50" cy="50" r="6" fill="var(--ab-accent)"/>
            <path d="M24 74L76 26" stroke="var(--ab-accent)" stroke-width="2" stroke-dasharray="3 3"/>
        </svg>"""
    },
    "linguist": {
        "title": "🗣️ خبير لغات ومترجم",
        "category": "humanities",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <circle cx="50" cy="50" r="26" stroke="var(--ab-gold)" stroke-width="3" fill="none"/>
            <path d="M24 50H76M50 24C42 34 42 66 50 76M50 24C58 34 58 66 50 76" stroke="var(--ab-accent)" stroke-width="2.5"/>
            <path d="M32 33C40 37 60 37 68 33M32 67C40 63 60 63 68 67" stroke="var(--ab-gold)" stroke-width="2"/>
        </svg>"""
    },
    "artist": {
        "title": "🎨 فنان ومصمم مبدع",
        "category": "humanities",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M26 48C26 34 38 24 54 24C68 24 78 34 78 46C78 58 70 64 64 64C60 64 58 60 54 60C50 60 48 64 46 68C44 72 38 76 32 72C28 68 26 58 26 48Z" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="3"/>
            <circle cx="40" cy="36" r="4" fill="var(--ab-gold)"/>
            <circle cx="54" cy="34" r="4" fill="var(--ab-card-inset)"/>
            <circle cx="66" cy="42" r="4" fill="var(--ab-gold)"/>
            <circle cx="36" cy="52" r="5" fill="var(--ab-card-inset)"/>
        </svg>"""
    },
    "writer": {
        "title": "✒️ أديب وكاتب مبدع",
        "category": "humanities",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 22L66 38L42 72L26 74L28 58L50 22Z" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="3" stroke-linejoin="round"/>
            <path d="M44 28L60 44" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <circle cx="36" cy="64" r="3" fill="var(--ab-gold)"/>
            <path d="M26 74L74 74" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round"/>
        </svg>"""
    },
    "astronomer": {
        "title": "🔭 فلكي ومستكشف فضاء",
        "category": "tech",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <circle cx="50" cy="50" r="16" fill="var(--ab-gold)"/>
            <ellipse cx="50" cy="50" rx="32" ry="10" stroke="var(--ab-accent)" stroke-width="3.5" transform="rotate(-25 50 50)" fill="none"/>
            <circle cx="28" cy="30" r="2.5" fill="var(--ab-gold)"/>
            <circle cx="72" cy="26" r="2" fill="var(--ab-gold)"/>
            <circle cx="68" cy="70" r="3" fill="var(--ab-accent)"/>
        </svg>"""
    },
    "neuro": {
        "title": "🧠 باحث في علوم الدماغ",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 26C42 26 34 30 32 38C28 42 28 50 32 56C30 62 34 70 42 72C46 73 50 70 50 68C50 70 54 73 58 72C66 70 70 62 68 56C72 50 72 42 68 38C66 30 58 26 50 26Z" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-accent)"/>
            <path d="M50 28V68M40 38C44 42 46 48 44 54M60 38C56 42 54 48 56 54" stroke="var(--ab-card-inset)" stroke-width="2.5" stroke-linecap="round"/>
        </svg>"""
    },
    "champion": {
        "title": "🏆 بطل ومثابر متألق",
        "category": "humanities",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M34 26H66V46C66 56 58 64 50 64C42 64 34 56 34 46V26Z" fill="var(--ab-gold)" stroke="var(--ab-accent)" stroke-width="2.5"/>
            <path d="M34 32H24C24 44 32 48 34 48" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M66 32H76C76 44 68 48 66 48" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M50 64V72M38 74H62" stroke="var(--ab-accent)" stroke-width="4" stroke-linecap="round"/>
            <circle cx="50" cy="42" r="5" fill="var(--ab-card-inset)"/>
        </svg>"""
    },
    "nature": {
        "title": "🌿 باحث بيئي وعلوم حيوية",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 74C50 74 48 54 34 44C26 38 26 26 38 26C52 26 50 48 50 48" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <path d="M50 66C50 66 54 50 66 42C74 36 74 26 62 26C48 26 50 50 50 50" fill="var(--ab-gold)" stroke="var(--ab-accent)" stroke-width="2.5"/>
            <path d="M50 76V48" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round"/>
        </svg>"""
    },
    "historian": {
        "title": "🏛️ مؤرخ وباحث آثار",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M24 38L50 24L76 38V42H24V38Z" fill="var(--ab-gold)"/>
            <path d="M28 42V68M42 42V68M58 42V68M72 42V68" stroke="var(--ab-accent)" stroke-width="3.5" stroke-linecap="round"/>
            <path d="M22 68H78V76H22V68Z" fill="var(--ab-gold)"/>
        </svg>"""
    },
    "pilot": {
        "title": "✈️ طيار وملاح جوي",
        "category": "tech",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 20L56 42L82 54L82 60L56 52L56 70L64 76L64 80L50 77L36 80L36 76L44 70L44 52L18 60L18 54L44 42L50 20Z" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="2.5" stroke-linejoin="round"/>
        </svg>"""
    },
    "morning_sun": {
        "title": "☀️ شمس الصباح الباكر (طاقة ونشاط)",
        "category": "humanities",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <circle cx="50" cy="50" r="18" fill="var(--ab-gold)"/>
            <path d="M50 18V26M50 74V82M18 50H26M74 50H82M27 27L33 33M67 67L73 73M27 73L33 67M67 33L73 27" stroke="var(--ab-accent)" stroke-width="4" stroke-linecap="round"/>
        </svg>"""
    },
    "night_owl": {
        "title": "🦉 بومة المذاكرة الليلية (سهر وتركيز)",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M32 30C32 24 38 22 42 28C46 26 54 26 58 28C62 22 68 24 68 30C72 38 72 64 64 74H36C28 64 28 38 32 30Z" fill="var(--ab-card-inset)" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <circle cx="42" cy="44" r="8" fill="var(--ab-gold)"/>
            <circle cx="58" cy="44" r="8" fill="var(--ab-gold)"/>
            <circle cx="42" cy="44" r="4" fill="var(--ab-accent)"/>
            <circle cx="58" cy="44" r="4" fill="var(--ab-accent)"/>
            <path d="M47 50L50 56L53 50Z" fill="var(--ab-accent)"/>
            <path d="M26 76H74" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round"/>
        </svg>"""
    },
    "pharmacist": {
        "title": "💊 صيدلي وخبير دواء",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <rect x="28" y="44" width="44" height="24" rx="12" transform="rotate(-35 50 56)" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <path d="M38 38L62 74" stroke="var(--ab-card-inset)" stroke-width="2.5"/>
            <circle cx="68" cy="32" r="3.5" fill="var(--ab-gold)"/>
            <circle cx="32" cy="68" r="2.5" fill="var(--ab-gold)"/>
        </svg>"""
    },
    "surgeon": {
        "title": "🔪 جراح ومشرط دقيق",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <circle cx="50" cy="42" r="16" fill="var(--ab-gold)"/>
            <rect x="34" y="42" width="32" height="14" rx="4" fill="var(--ab-card-inset)" stroke="var(--ab-accent)" stroke-width="2"/>
            <path d="M28 78C28 66 38 60 50 60C62 60 72 66 72 78" fill="var(--ab-accent)"/>
            <path d="M68 28L78 38L48 68L40 68L40 60L68 28Z" fill="var(--ab-gold)" stroke="var(--ab-card-inset)" stroke-width="1.5"/>
        </svg>"""
    },
    "dentist": {
        "title": "🦷 طبيب أسنان",
        "category": "medical",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M36 28C28 32 28 44 32 54C34 60 38 74 44 76C48 78 48 64 50 64C52 64 52 78 56 76C62 74 66 60 68 54C72 44 72 32 64 28C58 24 54 30 50 30C46 30 42 24 36 28Z" fill="var(--ab-card-inset)" stroke="var(--ab-gold)" stroke-width="3"/>
            <path d="M38 38C44 42 56 42 62 38" stroke="var(--ab-accent)" stroke-width="2.5" stroke-linecap="round"/>
        </svg>"""
    },
    "psychologist": {
        "title": "🧘 باحث في علم النفس",
        "category": "humanities",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M50 26C40 26 34 32 34 42C34 50 40 56 44 60V74H56V60C60 56 66 50 66 42C66 32 60 26 50 26Z" fill="var(--ab-accent)" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <circle cx="50" cy="42" r="6" fill="var(--ab-gold)"/>
            <path d="M30 76H70" stroke="var(--ab-gold)" stroke-width="3" stroke-linecap="round"/>
        </svg>"""
    },
    "software_eng": {
        "title": "💻 مهندس برمجيات وذكاء اصطناعي",
        "category": "tech",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <rect x="24" y="28" width="52" height="38" rx="5" fill="var(--ab-card-inset)" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <path d="M34 44L40 50L34 56M46 56H54" stroke="var(--ab-accent)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M38 66L32 74H68L62 66" stroke="var(--ab-gold)" stroke-width="2.5"/>
        </svg>"""
    },
    "bookworm": {
        "title": "📖 باحث نهِم وخبير مراجع",
        "category": "academic",
        "svg": """<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="var(--ab-gold)" stroke-width="3" fill="var(--ab-card-inset)"/>
            <path d="M26 68V36C34 34 42 36 50 40C58 36 66 34 74 36V68C66 66 58 68 50 72C42 68 34 66 26 68Z" fill="var(--ab-card-inset)" stroke="var(--ab-gold)" stroke-width="3"/>
            <path d="M50 40V72" stroke="var(--ab-gold)" stroke-width="2.5"/>
            <path d="M32 46H44M32 54H42M58 46H70M58 54H68" stroke="var(--ab-accent)" stroke-width="2" stroke-linecap="round"/>
        </svg>"""
    }
}



def get_theme_palette(theme_id: str) -> Dict[str, str]:
    """Returns color dictionary for the given theme."""
    return THEME_PALETTES.get(theme_id, THEME_PALETTES["coffee_mocha"])

def get_user_avatar_html(cfg: Dict[str, Any]) -> str:
    """Returns HTML for the user's avatar (either custom image or preset SVG)."""
    custom_path = cfg.get("custom_avatar_path", "")
    if custom_path and os.path.exists(custom_path):
        import base64
        try:
            with open(custom_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode("utf-8")
                ext = os.path.splitext(custom_path)[1].lower().replace(".", "")
                if ext == "svg":
                    mime = "image/svg+xml"
                elif ext in ("jpg", "jpeg"):
                    mime = "image/jpeg"
                else:
                    mime = "image/png"
                return f'<img src="data:{mime};base64,{b64}" class="user-custom-avatar" style="width:100%; height:100%; object-fit:cover; border-radius:50%; border:2px solid var(--ab-gold);" />'
        except Exception as e:
            print(f"[AnkiBiotic] Error loading custom avatar: {e}")

    av_type = cfg.get("avatar_type", "default")
    if av_type in AVATAR_PRESETS:
        return AVATAR_PRESETS[av_type]["svg"]
    return AVATAR_PRESETS["default"]["svg"]


# Font presets for typography customization
FONTS: Dict[str, Dict[str, Any]] = {
    "cairo": {
        "name": "Cairo (الافتراضي)",
        "css": "'Cairo', 'Segoe UI', Tahoma, sans-serif",
        "google": "Cairo:wght@400;600;700;800;900"
    },
    "tajawal": {
        "name": "Tajawal (تجوال)",
        "css": "'Tajawal', 'Segoe UI', sans-serif",
        "google": "Tajawal:wght@400;500;700;800"
    },
    "almarai": {
        "name": "Almarai (المراعي)",
        "css": "'Almarai', 'Segoe UI', sans-serif",
        "google": "Almarai:wght@400;700;800"
    },
    "alexandria": {
        "name": "Alexandria (الإسكندرية)",
        "css": "'Alexandria', 'Segoe UI', sans-serif",
        "google": "Alexandria:wght@400;600;700;800"
    },
    "system": {
        "name": "System UI (خط النظام)",
        "css": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "google": None
    },
}

# Default configuration values for AnkiBiotic
DEFAULTS: Dict[str, Any] = {
    "enabled": True,
    "theme": "coffee_mocha",
    "language": "ar",
    "daily_goal_enabled": True,
    "daily_goal_cards": 100,
    "show_eta": True,
    "font_family_preset": "cairo",
    "ui_scale": 100,
    "custom_colors": {
        "bg": "#1c1410",
        "card_bg": "#2a1e17",
        "card_inset": "#36271e",
        "accent": "#d4a373",
        "accent_hover": "#e6be94",
        "gold": "#e9b872",
        "fg": "#faedcd",
        "fg_subtle": "#b09785",
        "border": "#433024",
        "heatmap_color": "#d4a373",
        "heatmap_color_zero": "#2e2119",
        "heatmap_streak": "#e9b872",
        "new_color": "#6aa84f",
        "learn_color": "#e69138",
        "due_color": "#45818e"
    },
    "sidebar_width": 320,
    "sidebar_position": "right",
    "heatmap_weeks": 52,
    "card_radius": 16,
    "card_blur": 12,
    "card_opacity": 0.94,
    "font_family": "'Cairo', 'Segoe UI', Tahoma, sans-serif",
    "user_name": "المستخدم",
    "profile_subtitle": "طالب علم ومراجع متميز",
    "avatar_type": "default",
    "custom_avatar_path": "",
    "profile_pic_svg": "",
    "default_heatmap_view": "year",
    "start_of_week": "sunday",
    "show_streak": True,
    "show_quick_nav": True,
    "decks_default_collapsed": False,
    "show_stat_studied": True,
    "show_stat_retention": True,
    "show_stat_pace": True,
    "show_stat_time": True,
    "show_badges": True,
    "badges_default_collapsed": True,
}

_CONFIG_CACHE = None

def get_config_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "config.json")


def load_config() -> Dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    path = get_config_path()
    cfg = dict(DEFAULTS)
    # Deep copy custom_colors
    cfg["custom_colors"] = dict(DEFAULTS["custom_colors"])
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    for k, v in saved.items():
                        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                            cfg[k].update(v)
                        else:
                            cfg[k] = v
        except Exception as e:
            print(f"[AnkiBiotic] Error loading config: {e}")

    _CONFIG_CACHE = cfg
    return cfg

def save_config(new_cfg: Dict[str, Any]) -> None:
    global _CONFIG_CACHE
    _CONFIG_CACHE = new_cfg
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(new_cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[AnkiBiotic] Error saving config: {e}")

def invalidate_cache() -> None:
    global _CONFIG_CACHE
    _CONFIG_CACHE = None

def reset_config() -> None:
    global _CONFIG_CACHE
    _CONFIG_CACHE = None
    path = get_config_path()
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            print(f"[AnkiBiotic] Error resetting config: {e}")

def get_available_themes() -> Dict[str, str]:
    """Returns dict of theme_id -> display name."""
    return dict(THEMES)

def get_day_themes() -> Dict[str, str]:
    """Returns dict of Day/Light mode themes."""
    return dict(LIGHT_THEMES)

def get_night_themes() -> Dict[str, str]:
    """Returns dict of Night/Dark mode themes."""
    return dict(DARK_THEMES)

def is_theme_light(theme_id: str) -> bool:
    """Check if the theme is a Day/Light mode theme."""
    return theme_id in LIGHT_THEMES

def get_available_fonts() -> Dict[str, Dict[str, Any]]:
    """Returns all available font presets."""
    return dict(FONTS)

def get_font_info(font_key: str) -> Dict[str, Any]:
    """Returns font info dictionary for given font key."""
    return FONTS.get(font_key, FONTS["cairo"])

