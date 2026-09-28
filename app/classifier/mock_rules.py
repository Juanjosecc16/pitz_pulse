"""Keyword heuristics used by the mock client.

Deliberately simple: they let the project run end to end without an API key.
They are not meant to match the quality of the real model.
"""

import re
import unicodedata

from app.domain.enums import Category, Language, Priority, SuggestedArea

SHORT_MESSAGE_WORDS = 8

PORTUGUESE_MARKERS = {
    "oi", "pessoal", "preciso", "uma", "umas", "um", "voce", "nao", "dele", "dela", "pra", "falou",
    "hoje", "estao", "ja", "qual", "perguntou", "eu", "mando", "leva", "algumas", "obrigado",
}
SPANISH_MARKERS = {
    "hola", "equipo", "necesito", "una", "ustedes", "ayer", "sale", "puede", "pueden", "dice",
    "cuantos", "tenemos", "oigan", "seria", "genial", "veces", "lo", "le", "el", "gracias",
}
PORTUGUESE_CHARACTERS = "ãõç"
SPANISH_CHARACTERS = "ñ¿¡"

# Checked in order: the first category with a matching keyword wins.
CATEGORY_KEYWORDS: list[tuple[Category, tuple[str, ...]]] = [
    (Category.ACCESS, ("acceso", "acesso", "permiso", "permissao", "contrasena", "senha", "login")),
    (Category.AUTOMATION, ("automatiz", "manualmente", "algo que", "todo dia", "todos los dias")),
    (Category.BUG, ("error", "erro", "falla", "no funciona", "nao funciona", "some", "desaparece",
                    "no aparece", "no me aparecen", "lenta", "lento", "errado", "incorrect",
                    "dos veces", "duas vezes", "duplicad")),
    (Category.DATA, ("planilha", "reporte", "relatorio", "cuantos", "quantos", "datos", "dados",
                     "metrica", "ventas", "vendas")),
    (Category.QUESTION, ("como", "cual", "qual", "diferencia", "diferenca", "duda", "duvida")),
]

HIGH_PRIORITY_KEYWORDS = (
    "urgente", "error 500", "clientes", "reclamacao", "reclamo", "finalizar compra", "checkout",
    "pago", "pagou", "reembolso", "nota fiscal", "notas fiscais", "cnpj",
)
LOW_PRIORITY_CATEGORIES = {Category.QUESTION, Category.AUTOMATION, Category.OTHER}

FRONTEND_KEYWORDS = ("boton", "botao", "pantalla", "tela", "celular", "movil", "navegador")
PERFORMANCE_KEYWORDS = ("lenta", "lento", "caido", "caiu")
NEEDS_INFO_KEYWORDS = ("no se", "nao sei")

AREA_BY_CATEGORY: dict[Category, SuggestedArea] = {
    Category.BUG: SuggestedArea.BACKEND,
    Category.DATA: SuggestedArea.DATA,
    Category.ACCESS: SuggestedArea.DEVOPS,
    Category.AUTOMATION: SuggestedArea.DIGITAL_TRANSFORMATION,
    Category.QUESTION: SuggestedArea.PRODUCT,
    Category.OTHER: SuggestedArea.PRODUCT,
}

FOLLOW_UP_QUESTIONS: dict[Language, str] = {
    Language.SPANISH: "¿Puedes darnos más detalle: qué ocurre exactamente, desde cuándo y a quién afecta?",
    Language.PORTUGUESE: "Pode dar mais detalhes: o que acontece exatamente, desde quando e quem é afetado?",
}


def normalize(text: str) -> str:
    """Lowercase and remove accents so keywords match regardless of spelling."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def contains_any(normalized_text: str, keywords) -> bool:
    return any(re.search(rf"\b{re.escape(keyword)}", normalized_text) for keyword in keywords)


def detect_language(message: str) -> Language:
    words = set(re.findall(r"\w+", normalize(message)))
    portuguese_score = len(words & PORTUGUESE_MARKERS) + 2 * sum(message.count(c) for c in PORTUGUESE_CHARACTERS)
    spanish_score = len(words & SPANISH_MARKERS) + 2 * sum(message.count(c) for c in SPANISH_CHARACTERS)
    return Language.PORTUGUESE if portuguese_score > spanish_score else Language.SPANISH


def detect_category(normalized_text: str) -> Category:
    for category, keywords in CATEGORY_KEYWORDS:
        if contains_any(normalized_text, keywords):
            return category
    return Category.QUESTION if "?" in normalized_text else Category.OTHER


def detect_priority(normalized_text: str, category: Category) -> Priority:
    if contains_any(normalized_text, HIGH_PRIORITY_KEYWORDS):
        return Priority.HIGH
    return Priority.LOW if category in LOW_PRIORITY_CATEGORIES else Priority.MEDIUM


def detect_area(normalized_text: str, category: Category) -> SuggestedArea:
    if category is Category.BUG and contains_any(normalized_text, FRONTEND_KEYWORDS):
        return SuggestedArea.FRONTEND
    if category is Category.BUG and contains_any(normalized_text, PERFORMANCE_KEYWORDS):
        return SuggestedArea.DEVOPS
    return AREA_BY_CATEGORY[category]


def detect_needs_info(normalized_text: str) -> bool:
    return len(normalized_text.split()) < SHORT_MESSAGE_WORDS or contains_any(normalized_text, NEEDS_INFO_KEYWORDS)
