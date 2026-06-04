import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import common_args, log_utils
from config import config_io, runtime
from config.deck_translator_config import DeckTranslatorConfig
from deck_translator import translator_common
from deck_translator.translator_common import Deck
from deck_translator import translator_pipeline
import argparse
import logging

logger = logging.getLogger(__name__)

def main() -> None:
    try:
        runtime.initialize_runtime(translator_common.DECK_TRANSLATOR_LOG_NAME)

        cli_args = parse_cli_args()

        translator_config = config_io.build_deck_translator_config()
        apply_cli_args(args=cli_args, config=translator_config)

        deck: Deck = translator_pipeline.build_deck(deck_name="ForgeDeck") # placeholder deck name
        translator_pipeline.write_translated_deck(deck=deck, file_name="mydeck") # placeholder file name

        logger.info("Finished execution without error.")
        
    except Exception:
        log_utils.log_unexpected_and_exit()
        
def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="deck-translator",
        description="Translate decks between Shandalar and MTG: Forge formats.",
        epilog=(
            "Examples:\n"
            "  %(prog)s\n"
            "  %(prog)s -s full"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    common_args.add_encoding_scan_argument(parser)

    return parser.parse_args()

def apply_cli_args(args: argparse.Namespace, config: DeckTranslatorConfig) -> None:
    # Stub pending implementation.
    pass

if __name__ == "__main__":
    main()