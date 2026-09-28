import pytest

from app.classifier.sanitizer import mask_sensitive_data


@pytest.mark.parametrize(
    ("sensitive_value", "placeholder"),
    [
        ("12.345.678/0001-90", "[CNPJ]"),
        ("12345678000190", "[CNPJ]"),
        ("123.456.789-09", "[CPF]"),
        ("ana.lopez@pitz.com", "[EMAIL]"),
        ("4111 1111 1111 1111", "[TARJETA]"),
        ("GODE561231GR8", "[RFC]"),
    ],
)
def test_masks_sensitive_values(sensitive_value, placeholder):
    masked = mask_sensitive_data(f"Dato del cliente: {sensitive_value}. Gracias.")

    assert masked == f"Dato del cliente: {placeholder}. Gracias."


def test_keeps_regular_text_and_small_numbers():
    text = "Error 500 al subir el catálogo; van 3 casos este mes."

    assert mask_sensitive_data(text) == text
