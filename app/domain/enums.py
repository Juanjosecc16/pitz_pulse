"""Allowed values for every classification field.

Member names are in English (used in code); values are the Spanish labels
required by the case specification (used in JSON, database and prompt).
This is the single source of truth: adding a category means adding one line here.
"""

from enum import StrEnum


class Category(StrEnum):
    BUG = "bug"
    DATA = "datos"
    ACCESS = "acceso"
    AUTOMATION = "automatizacion"
    QUESTION = "consulta"
    OTHER = "otro"


class Priority(StrEnum):
    HIGH = "alta"
    MEDIUM = "media"
    LOW = "baja"


class SuggestedArea(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATA = "data"
    DEVOPS = "devops"
    PRODUCT = "producto"
    DIGITAL_TRANSFORMATION = "digital_transformation"


class Language(StrEnum):
    SPANISH = "es"
    PORTUGUESE = "pt"
