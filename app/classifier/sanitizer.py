"""Masks personal and fiscal data before a message leaves our infrastructure."""

import re

# Order matters: longer / more specific patterns first.
SENSITIVE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[EMAIL]"),
    (re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"), "[CNPJ]"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[TARJETA]"),
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF]"),
    (re.compile(r"\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}\b"), "[RFC]"),
]


def mask_sensitive_data(text: str) -> str:
    for pattern, placeholder in SENSITIVE_PATTERNS:
        text = pattern.sub(placeholder, text)
    return text
