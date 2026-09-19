"""Small, source-text based client localization layer.

English UI text remains the canonical source in the application code. A locale
catalog maps that source text to a translation at runtime; missing entries fall
back to English. This keeps localization changes shallow and makes upstream
merges much less conflict-prone than replacing literals in-place.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_LANGUAGE = "zh_CN"
SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh_CN": "简体中文",
}

_LANGUAGE = DEFAULT_LANGUAGE
_CATALOG: dict[str, str] = {}
_TEMPLATES: list[tuple[re.Pattern[str], list[str], str]] = []
_PLACEHOLDER = re.compile(r"\{([A-Za-z_]\w*)(?::[^}]*)?\}")


def _locale_path(language: str) -> Path:
    # Locales live under assets so the existing PyInstaller --add-data rule
    # carries them into portable builds without touching the release pipeline.
    return Path(__file__).with_name("assets") / "locales" / f"{language}.json"


def _compile_template(source: str, translated: str):
    names: list[str] = []
    pieces: list[str] = []
    cursor = 0
    for match in _PLACEHOLDER.finditer(source):
        pieces.append(re.escape(source[cursor:match.start()]))
        name = match.group(1)
        names.append(name)
        pieces.append(f"(?P<{name}>.+?)")
        cursor = match.end()
    pieces.append(re.escape(source[cursor:]))
    return re.compile("^" + "".join(pieces) + "$", re.DOTALL), names, translated


def set_language(language: str | None) -> str:
    """Select a language. Unknown/missing catalogs safely fall back to English."""
    global _LANGUAGE, _CATALOG, _TEMPLATES
    requested = (language or DEFAULT_LANGUAGE).replace("-", "_")
    if requested.lower().startswith("zh"):
        requested = "zh_CN"
    elif requested.lower().startswith("en"):
        requested = "en"

    _LANGUAGE = requested if requested in SUPPORTED_LANGUAGES else "en"
    _CATALOG = {}
    _TEMPLATES = []
    if _LANGUAGE == "en":
        return _LANGUAGE

    try:
        payload = json.loads(_locale_path(_LANGUAGE).read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            _CATALOG = {
                str(source): str(target)
                for source, target in payload.items()
                if isinstance(source, str) and isinstance(target, str) and target
            }
    except (OSError, ValueError, TypeError):
        _LANGUAGE = "en"
        return _LANGUAGE

    for source, translated in _CATALOG.items():
        if _PLACEHOLDER.search(source):
            try:
                _TEMPLATES.append(_compile_template(source, translated))
            except re.error:
                pass
    return _LANGUAGE


def get_language() -> str:
    return _LANGUAGE


def available_languages() -> tuple[tuple[str, str], ...]:
    return tuple(SUPPORTED_LANGUAGES.items())


def tr(text: str, /, **values) -> str:
    """Translate UI text, falling back to the original English source string."""
    if not isinstance(text, str) or not text or _LANGUAGE == "en":
        return text.format(**values) if values else text

    translated = _CATALOG.get(text)
    if translated is not None:
        if values:
            try:
                return translated.format(**values)
            except (KeyError, ValueError):
                return translated
        return translated

    for pattern, names, target in _TEMPLATES:
        match = pattern.match(text)
        if match:
            captured = {name: match.group(name) for name in names}
            try:
                return target.format(**captured)
            except (KeyError, ValueError):
                return target

    return text.format(**values) if values else text


set_language(DEFAULT_LANGUAGE)
