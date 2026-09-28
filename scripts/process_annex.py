"""Classify the Annex A messages and write resultados.json.

Usage (from the project root):
    python -m scripts.process_annex [--input data/mensajes.json] [--output resultados.json]
"""

import argparse
import logging
import sys
from pathlib import Path

from app.batch import classify_messages, load_messages, write_results
from app.classifier.factory import create_classifier_service
from app.core.config import get_settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify a JSON file of internal requests.")
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "mensajes.json")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "resultados.json")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    settings = get_settings()
    model_info = f" | model: {settings.llm_model}" if settings.llm_provider != "mock" else " (no LLM calls)"
    logging.info("Provider: %s%s", settings.llm_provider, model_info)

    messages = load_messages(args.input)
    result = classify_messages(create_classifier_service(settings), messages)
    write_results(args.output, result.classifications)

    logging.info("Wrote %d/%d classifications to %s", len(result.classifications), len(messages), args.output)
    if result.failed_ids:
        logging.error("Failed messages: %s", ", ".join(result.failed_ids))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
