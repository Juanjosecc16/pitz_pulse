"""Domain models and their validation rules.

Attributes are named in English; aliases map them to the Spanish JSON keys
required by the case specification. Models accept both names on input and
always serialize using the aliases.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.enums import Category, Language, Priority, SuggestedArea

MAX_SUMMARY_WORDS = 20
MAX_MESSAGE_LENGTH = 4000

ALIASED_MODEL_CONFIG = ConfigDict(
    validate_by_name=True,
    validate_by_alias=True,
    serialize_by_alias=True,
    str_strip_whitespace=True,
)


class Classification(BaseModel):
    """Structured triage result for a single internal request."""

    model_config = ALIASED_MODEL_CONFIG

    id: str = Field(min_length=1)
    category: Category = Field(alias="categoria")
    priority: Priority = Field(alias="prioridad")
    suggested_area: SuggestedArea = Field(alias="area_sugerida")
    language: Language = Field(alias="idioma")
    summary: str = Field(alias="resumen", min_length=1)
    needs_info: bool = Field(alias="requiere_info")
    follow_up_question: str | None = Field(default=None, alias="pregunta_seguimiento")

    @field_validator("summary")
    @classmethod
    def summary_within_word_limit(cls, summary: str) -> str:
        word_count = len(summary.split())
        if word_count > MAX_SUMMARY_WORDS:
            raise ValueError(f"summary has {word_count} words; maximum is {MAX_SUMMARY_WORDS}")
        return summary

    @model_validator(mode="after")
    def follow_up_matches_needs_info(self) -> "Classification":
        if self.needs_info and not self.follow_up_question:
            raise ValueError("follow_up_question is required when needs_info is true")
        if not self.needs_info:
            # A question without a need for info is noise; normalize it instead of failing.
            self.follow_up_question = None
        return self


class StoredRequest(Classification):
    """A classified request together with its original message, as persisted and listed by the API."""

    message: str
    source_area: str | None = None
    created_at: datetime


class RequestInput(BaseModel):
    """Payload used to submit a new internal request for classification."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    source_area: str | None = Field(default=None, max_length=100)
