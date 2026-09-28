"""Test doubles shared across test modules."""

import json

from app.classifier.base import ClassificationPrompt, LLMClient

VALID_LLM_OUTPUT = {
    "categoria": "bug",
    "prioridad": "alta",
    "area_sugerida": "backend",
    "idioma": "es",
    "resumen": "Vendedor recibe error 500 al subir su catálogo.",
    "requiere_info": False,
    "pregunta_seguimiento": None,
}


def valid_llm_output_text(**overrides) -> str:
    return json.dumps({**VALID_LLM_OUTPUT, **overrides}, ensure_ascii=False)


class ScriptedLLMClient(LLMClient):
    """Returns (or raises) the scripted responses in order and records every prompt."""

    def __init__(self, *responses: str | Exception):
        self._responses = list(responses)
        self.prompts: list[ClassificationPrompt] = []

    def complete(self, prompt: ClassificationPrompt) -> str:
        self.prompts.append(prompt)
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response
