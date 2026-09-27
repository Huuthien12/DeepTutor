"""Shared language directives for prompt-driven LLM calls.

This helper centralizes the "stay in the requested language" instruction so
different modules can share the same behavior without depending on book-only
utilities.
"""

from __future__ import annotations

import re

_LANGUAGE_LABELS: dict[str, str] = {
    "zh": "中文（简体）",
    "zh-cn": "中文（简体）",
    "zh-tw": "繁體中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "ru": "Русский",
    "pt": "Português",
    "it": "Italiano",
    "vi": "Vietnamese",
}

_VIETNAMESE_MARKERS = re.compile(
    r"[\u1ea0-\u1ef9\u0102\u0103\u00c2\u00e2\u0110\u0111\u00ca\u00ea\u00d4\u00f4"
    r"\u01a0\u01a1\u01af\u01b0\u00c0\u00c1\u00c8\u00c9\u00cc\u00cd\u00d2\u00d3"
    r"\u00d9\u00da\u00dd\u00e0\u00e1\u00e8\u00e9\u00ec\u00ed\u00f2\u00f3\u00f9"
    r"\u00fa\u00fd]"
)
_CHINESE_MARKERS = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
_ENGLISH_MARKERS = re.compile(r"[A-Za-z]")


def normalize_language(language: str | None) -> str:
    return (language or "en").strip().lower() or "en"


def detect_language(text: str, fallback: str | None = "en") -> str:
    """Detect supported query languages; preserve the requested fallback otherwise."""
    if _VIETNAMESE_MARKERS.search(text):
        return "vi"
    if _CHINESE_MARKERS.search(text):
        return "zh"
    return "en" if _ENGLISH_MARKERS.search(text) else normalize_language(fallback)


def language_label(language: str | None) -> str:
    code = normalize_language(language)
    if code in _LANGUAGE_LABELS:
        return _LANGUAGE_LABELS[code]
    base = code.split("-", 1)[0]
    return _LANGUAGE_LABELS.get(base, language or "English")


def language_directive(language: str | None) -> str:
    """Return a strict reader-facing language instruction for prompts."""
    code = normalize_language(language)
    label = language_label(code)
    if code.startswith("zh"):
        return (
            "\n\n[语言要求 / Language] "
            f"请严格使用{label}撰写所有面向读者的文本（标题、正文、解释、提示、过渡句、"
            "题干、选项等），即使参考资料、JSON 字段名或英文术语出现在 prompt 中也"
            "不得切换语言；保留必要的专有名词原文（如人名、产品名、公式中的变量符号"
            f"等）即可，其余一律使用{label}。"
        )
    if code == "en":
        return (
            "\n\n[Language] Write ALL reader-facing text (titles, prose, "
            "explanations, hints, transitions, quiz stems, options, etc.) in "
            "English. Do NOT switch languages even if the source material, "
            "JSON keys, or examples in this prompt are in another language. "
            "Keep proper nouns (people, products, formula symbols) in their "
            "original form."
        )
    return (
        f"\n\n[Language] Write ALL reader-facing text strictly in {label}. "
        "Do NOT switch languages even if the source material, JSON keys, or "
        "examples in this prompt are in a different language. Keep proper "
        "nouns (people, products, formula symbols) in their original form."
    )


def append_language_directive(system_prompt: str | None, language: str | None) -> str:
    """Append the language directive to an existing system prompt."""
    base = (system_prompt or "").rstrip()
    directive = language_directive(language).strip()
    if not base:
        return directive
    return f"{base}\n\n{directive}"


__all__ = [
    "append_language_directive",
    "detect_language",
    "language_directive",
    "language_label",
    "normalize_language",
]
