"""Turns raw model output into a validated Classification."""

import json
import re

from pydantic import ValidationError

from app.classifier.errors import InvalidLLMResponseError
from app.domain.models import Classification

CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_classification(raw_output: str, request_id: str) -> Classification:
    """Parse and validate the model output; the id always comes from our side."""
    data = _extract_json_object(raw_output)
    data["id"] = request_id
    try:
        return Classification.model_validate(data)
    except ValidationError as error:
        raise InvalidLLMResponseError(_describe_validation_error(error)) from error


def _extract_json_object(raw_output: str) -> dict:
    text = CODE_FENCE_PATTERN.sub("", raw_output.strip())
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise InvalidLLMResponseError("the response does not contain a JSON object")
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as error:
        raise InvalidLLMResponseError(f"the response is not valid JSON: {error.msg}") from error
    if not isinstance(data, dict):
        raise InvalidLLMResponseError("the response JSON is not an object")
    return data


def _describe_validation_error(error: ValidationError) -> str:
    problems = []
    for detail in error.errors():
        field = ".".join(str(part) for part in detail["loc"]) or "response"
        problems.append(f"{field}: {detail['msg']}")
    return "; ".join(problems)
