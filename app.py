"""
GenAI Discord Bot — Hybrid RAG + Vision Assistant

Entry point: python app.py
"""

import sys
import logging

# ── Logging setup ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-8s │ %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("app")


def main() -> None:
    logger.info("=" * 60)
    logger.info("  GenAI Discord Bot — Starting up...")
    logger.info("=" * 60)

    from bot.client import run_bot
    run_bot()


if __name__ == "__main__":
    main()
