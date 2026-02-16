# -*- coding: utf-8 -*-
import os, sys, json
import gradio as gr

# ======================================================================
# Wire to your working inference code (DON'T TOUCH THE MODEL FILE)
# ======================================================================
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT)
from BabyCryLast import analyze as core_analyze  # uses your stable logic

# ======================================================================
# Translations (UI + phrase-level postprocessing for results)
# ======================================================================
DEFAULT_TRANSLATIONS = {
    "en": {
        "brand": "KudakAI",
        "app_title": "KudakAI — Intelligent Cry Analyzer",
        "app_tagline": "Real-time cry interpretation and anomaly screening.",
        "upload_label": "Upload or Record Baby Cry",
        "analyze_btn": "Analyze",
        "result_label": "Analysis Result",
        "lang_label": "Language",
        "analyzer_header": "Cry Analyzer",
        "hospitals_header": "Nearby Hospitals",
        "about_header": "About KudakAI",
        "map_hint": "Nearest pediatric clinics and hospitals in your area.",
        "about_md": """
### What KudakAI does
- Classifies baby cry emotion from audio.
- Screens for atypical cry patterns using acoustic features.

### Notes
- This is **not** a medical diagnosis tool; it provides supportive signals.
- Avoid adult speech or music; the model will try to classify anything that resembles a cry.
""",
        "phrases": {
            "No cry detected": "No cry detected",
            "No cry pattern detected": "No cry pattern detected",
            "Detected:": "Detected:",
            "Typical cry pattern": "Typical cry pattern",
            "Atypical cry pattern": "Atypical cry pattern",
            "silence/background": "silence/background",
            "non-cry sound": "non-cry sound"
        },
        "tab_labels": {
            "analyze": "🔊 Analyzer",
            "hospitals": "🏥 Nearby Hospitals",
            "about": "ℹ️ About"
        },
        "footer": "Made by muslimercurii",
    },
    "tj": {
        "brand": "KudakAI",
        "app_title": "KudakAI — Таҳлилгари оқилонаи гиря",
        "app_tagline": "Тафсири фаврии гиря ва санҷиши намунаҳои ғайримуқаррарӣ.",
        "upload_label": "Гиряи кӯдакро бор ё сабт кунед",
        "analyze_btn": "Таҳлил",
        "result_label": "Натиҷаи таҳлил",
        "lang_label": "Забон",
        "analyzer_header": "Таҳлили гиря",
        "hospitals_header": "Беморхонаҳои наздик",
        "about_header": "Дар бораи KudakAI",
        "map_hint": "Клиникаҳо ва беморхонаҳои наздики кӯдакона дар минтақаи шумо.",
        "about_md": """
### Барнома чӣ кор мекунад
- Эҳсоси гиряи кӯдакро аз аудио муайян мекунад.
- Намунаҳои ғайримуқаррарии гиряро бо аломатҳои акустикӣ месанҷад.

### Эзоҳ
- Ин **асбоби ташхиси тиббӣ нест**; танҳо иттилооти иловагӣ медиҳад.
- Сухани калонсолон ё мусиқиро ворид накунед; модел ҳар чизеро, ки ба гиря монанд аст, тасниф мекунад.
""",
        "phrases": {
            "No cry detected": "Гиря муайян нашуд",
            "No cry pattern detected": "Намунаи гиря муайян нашуд",
            "Detected:": "Муайян шуд:",
            "Typical cry pattern": "Намунаи оддии гиря",
            "Atypical cry pattern": "Намунаи ғайримуқаррарии гиря",
            "silence/background": "хомӯшӣ/пасзамина",
            "non-cry sound": "садои ғайри гиря"
        },
        "tab_labels": {
            "analyze": "🔊 Таҳлил",
            "hospitals": "🏥 Беморхонаҳо",
            "about": "ℹ️ Дар бораи"
        },
        "footer": "Муаллиф: muslimercurii",
    },
    "ru": {
        "brand": "KudakAI",
        "app_title": "KudakAI — Интеллектуальный анализ плача",
        "app_tagline": "Онлайн-интерпретация плача и скрининг атипичных паттернов.",
        "upload_label": "Загрузить или записать плач ребёнка",
        "analyze_btn": "Анализ",
        "result_label": "Результат анализа",
        "lang_label": "Язык",
        "analyzer_header": "Анализ плача",
        "hospitals_header": "Ближайшие больницы",
        "about_header": "О KudakAI",
        "map_hint": "Ближайшие детские клиники и больницы в вашем районе.",
        "about_md": """
### Что делает приложение
- Классифицирует эмоциональное состояние по аудио плача.
- Проверяет на атипичные паттерны по акустическим признакам.

### Важно
- Это **не** медицинская диагностика; только вспомогательная информация.
- Не используйте речь взрослых или музыку; модель попытается классифицировать всё, что похоже на плач.
""",
        "phrases": {
            "No cry detected": "Плач не обнаружен",
            "No cry pattern detected": "Паттерн плача не обнаружен",
            "Detected:": "Обнаружено:",
            "Typical cry pattern": "Типичный паттерн плача",
            "Atypical cry pattern": "Атипичный паттерн плача",
            "silence/background": "тишина/фон",
            "non-cry sound": "звук не плача"
        },
        "tab_labels": {
            "analyze": "🔊 Анализ",
            "hospitals": "🏥 Больницы рядом",
            "about": "ℹ️ О проекте"
        },
        "footer": "Автор: muslimercurii"
    }
}
LABEL_TRANSLATIONS = {
    "ru": {
        "belly_pain": "Боль в животе",
        "burping": "Отрыжка",
        "discomfort": "Дискомфорт",
        "dont_know": "Неизвестно",
        "hungry": "Голод",
        "lonely": "Одиночество",
        "no_cry": "Без плача",
        "tired": "Усталость",
    },
    "tj": {
        "belly_pain": "Дарди шикам",
        "burping": "Дилаш боло шуд",
        "discomfort": "Нооромӣ",
        "dont_know": "Номаълум",
        "hungry": "Гурусна",
        "lonely": "Танҳо",
        "no_cry": "Бе гиря",
        "tired": "Хаста",
    },
}



TRANSLATIONS = DEFAULT_TRANSLATIONS

def tr(lang: str, key: str, fallback=""):
    return TRANSLATIONS.get(lang, DEFAULT_TRANSLATIONS["en"]).get(key, fallback)

def localize_result(text: str, lang: str) -> str:
    phrases = TRANSLATIONS.get(lang, DEFAULT_TRANSLATIONS["en"]).get("phrases", {})
    for en_snip, tr_snip in phrases.items():
        text = text.replace(en_snip, tr_snip)
    for en_label, tr_label in LABEL_TRANSLATIONS.get(lang, {}).items():
        text = text.replace(en_label, tr_label)
    return text