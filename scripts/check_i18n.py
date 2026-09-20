"""Report untranslated client UI strings without touching documentation.

This intentionally scans only Python client sources.  English remains canonical;
when upstream adds UI text, this script makes the missing zh-CN entries obvious
while the application itself safely falls back to English.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "dlss5_converter"
CATALOG = PACKAGE / "assets" / "locales" / "zh_CN.json"

CALLS = {
    "QPushButton", "QLabel", "QCheckBox", "QGroupBox", "ModuleCard",
    "SliderRow", "TourStep", "stage_placeholder",
}
METHODS = {
    "setWindowTitle", "setToolTip", "setText", "showMessage", "setFormat",
    "setPlaceholderText", "information", "warning", "critical", "question",
    "getOpenFileName", "getOpenFileNames", "getSaveFileName",
    "getExistingDirectory",
}
SKIP_FILES = {"i18n.py", "i18n_widgets.py"}

# Intentional non-translatable display tokens, or composite strings whose
# human-readable pieces are translated before interpolation. Keeping these out
# of the report lets the check fail only on real missing client copy.
IGNORE_STRINGS = {
    "%p%",
    "DLSS<span style=\"color:{signal};\">·</span>5&nbsp;&nbsp;IMAGE&nbsp;&amp;&nbsp;VIDEO&nbsp;CONVERTER",
    "GitHub",
    "N",
    "v{__version__}",
    "{self._index + 1} · {tr(step.title)}",
    "{tr(label)}  {row.formatted(value)}",
}


def _name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _expr_text(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for item in node.values:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                parts.append(item.value)
            elif isinstance(item, ast.FormattedValue):
                try:
                    expr = ast.unparse(item.value)
                except Exception:
                    expr = "value"
                parts.append("{" + expr + "}")
        return "".join(parts)
    return None


def _visible_args(call: ast.Call) -> list[ast.AST]:
    name = _name(call.func)
    if name in CALLS:
        if name == "SliderRow":
            return [arg for index, arg in enumerate(call.args) if index in (0, 3)]
        if name == "TourStep":
            return list(call.args[:2])
        if name == "stage_placeholder":
            return list(call.args[1:3])
        return list(call.args[:1])
    if name in METHODS:
        if name in {"information", "warning", "critical", "question"}:
            return list(call.args[1:3])
        if name.startswith("get"):
            return list(call.args[1:2])
        return list(call.args[:1])
    if name == "addTab":
        return list(call.args[-1:])
    return []


def collect() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in sorted(PACKAGE.glob("*.py")):
        if path.name in SKIP_FILES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for arg in _visible_args(node):
                text = _expr_text(arg)
                if not text or not any(ch.isalpha() for ch in text):
                    continue
                found.setdefault(text, []).append(
                    f"{path.relative_to(ROOT)}:{getattr(node, 'lineno', '?')}"
                )
    return found


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    found = collect()
    missing = {
        text: where
        for text, where in found.items()
        if text not in catalog and text not in IGNORE_STRINGS
    }

    print(f"client strings detected : {len(found)}")
    print(f"zh-CN catalog entries   : {len(catalog)}")
    print(f"missing translations    : {len(missing)}")
    if missing:
        print()
        for text, where in sorted(missing.items()):
            print(f"- {text!r}")
            print(f"  {', '.join(where)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
