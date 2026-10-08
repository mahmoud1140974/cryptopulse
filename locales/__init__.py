"""Translations for CryptoPulse bot."""

from __future__ import annotations

import importlib
import logging

logger = logging.getLogger(__name__)

# Codes des langues supportées
SUPPORTED_LANGS = ["en", "fr", "es", "pt", "ar", "ru", "id", "tr"]

DEFAULT_LANG = "en"

LANG_LABELS = {
    "en": "🇬🇧 English",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "pt": "🇵🇹 Português",
    "ar": "🇸🇦 العربية",
    "ru": "🇷🇺 Русский",
    "id": "🇮🇩 Indonesia",
    "tr": "🇹🇷 Türkçe",
}


def _load_strings(code: str) -> dict:
    """
    Charge dynamiquement les chaînes d'une langue.
    Si le module n'existe pas encore, renvoie {} sans crasher.
    """
    try:
        mod = importlib.import_module(f".{code}", package=__name__)
        return getattr(mod, "STRINGS", {}) or {}
    except Exception as exc:
        logger.warning("locales: could not load '%s': %s", code, exc)
        return {}


# Chargement de toutes les langues (fallback vide si absent)
LANGUAGES: dict[str, dict] = {code: _load_strings(code) for code in SUPPORTED_LANGS}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """
    Retourne une chaîne traduite.
    Fallback sur l'anglais si la clé n'existe pas dans la langue demandée.
    Fallback sur la clé elle-même si rien n'est trouvé.
    """
    lang = (lang or DEFAULT_LANG).lower()
    strings = LANGUAGES.get(lang) or {}
    text = strings.get(key) or LANGUAGES.get(DEFAULT_LANG, {}).get(key) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def is_supported(lang: str) -> bool:
    return (lang or "").lower() in SUPPORTED_LANGS
