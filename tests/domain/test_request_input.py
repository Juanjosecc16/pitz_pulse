import pytest
from pydantic import ValidationError

from app.domain.models import MAX_MESSAGE_LENGTH, RequestInput


def test_strips_message_whitespace():
    request = RequestInput(message="  Oigan, la plataforma está lenta.  ", source_area="Operaciones MX")

    assert request.message == "Oigan, la plataforma está lenta."


def test_source_area_is_optional():
    assert RequestInput(message="Hola").source_area is None


@pytest.mark.parametrize("message", ["", "    "])
def test_rejects_empty_message(message):
    with pytest.raises(ValidationError):
        RequestInput(message=message)


def test_rejects_message_over_max_length():
    with pytest.raises(ValidationError):
        RequestInput(message="a" * (MAX_MESSAGE_LENGTH + 1))
