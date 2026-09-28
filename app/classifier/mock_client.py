"""Offline LLMClient that classifies with keyword rules (LLM_PROVIDER=mock).

It returns the same JSON text a real model would, so the parser and the
validation run exactly as in production.
"""

import json

from app.classifier import mock_rules
from app.classifier.base import ClassificationPrompt, LLMClient


class MockLLMClient(LLMClient):
    def complete(self, prompt: ClassificationPrompt) -> str:
        text = mock_rules.normalize(prompt.message)
        language = mock_rules.detect_language(prompt.message)
        category = mock_rules.detect_category(text)
        priority = mock_rules.detect_priority(text, category)
        needs_info = mock_rules.detect_needs_info(text)

        return json.dumps(
            {
                "categoria": category.value,
                "prioridad": priority.value,
                "area_sugerida": mock_rules.detect_area(text, category).value,
                "idioma": language.value,
                "resumen": f"Solicitud clasificada como {category.value} con prioridad {priority.value} (modo mock, sin IA).",
                "requiere_info": needs_info,
                "pregunta_seguimiento": mock_rules.FOLLOW_UP_QUESTIONS[language] if needs_info else None,
            },
            ensure_ascii=False,
        )
