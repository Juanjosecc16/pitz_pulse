"""JSON schema the model must follow, generated from the domain enums.

The schema covers structure and allowed values. Rules the schema language
cannot express (20-word summary, needs_info/question coherence) are still
enforced by the Pydantic model after parsing.
"""

from app.domain.enums import Category, Language, Priority, SuggestedArea


def _enum_values(enum_class) -> list[str]:
    return [member.value for member in enum_class]


CLASSIFICATION_OUTPUT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "categoria": {"type": "string", "enum": _enum_values(Category)},
        "prioridad": {"type": "string", "enum": _enum_values(Priority)},
        "area_sugerida": {"type": "string", "enum": _enum_values(SuggestedArea)},
        "idioma": {"type": "string", "enum": _enum_values(Language)},
        "resumen": {"type": "string"},
        "requiere_info": {"type": "boolean"},
        "pregunta_seguimiento": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
    "required": [
        "categoria",
        "prioridad",
        "area_sugerida",
        "idioma",
        "resumen",
        "requiere_info",
        "pregunta_seguimiento",
    ],
    "additionalProperties": False,
}
