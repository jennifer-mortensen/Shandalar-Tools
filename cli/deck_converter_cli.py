"""
Command-line entry point for the Shandalar Tools deck converter.

Initializes shared runtime services, loads configuration, applies
command-line overrides, and executes deck conversion between
supported deck formats.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import args_defs, log_utils, runtime
from resources import config_loader
from resources.deck_converter_config import DeckConverterConfig
from mtg.deck import Deck
from pipeline import deck_converter_const, deck_converter_pipeline
import argparse
import logging

logger = logging.getLogger(__name__)

def main() -> None:
    """
    Execute the deck converter command-line workflow.

    Initializes runtime services, loads configuration, applies any
    command-line overrides, performs deck conversion, and writes the
    translated deck to disk.

    Exits with a logged error message if an unexpected exception occurs.
    """    
    try:
        runtime.initialize_runtime(deck_converter_const.LOG_NAME)

        cli_args = parse_cli_args()

        config = config_loader.get_deck_converter_config()
        apply_cli_args(args=cli_args, config=config)

        deck: Deck = deck_converter_pipeline.build_deck(deck_name="ForgeDeck")         # placeholder deck name
        deck_converter_pipeline.write_translated_deck(deck=deck, file_name="ShandalarDeck") # placeholder file name

        logger.info("Finished execution without error.")
        
    except Exception:
        log_utils.log_unexpected_and_exit()
        
def parse_cli_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the deck converter.

    Defines supported command-line options and returns the parsed
    argument namespace.

    Returns:
        Parsed command-line arguments.
    """    
    parser = argparse.ArgumentParser(
        prog=deck_converter_const.CLI_PROG,
        description=deck_converter_const.CLI_DESCRIPTION,
        epilog=deck_converter_const.CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    args_defs.add_encoding_scan_mode_argument(parser)

    return parser.parse_args()

def apply_cli_args(args: argparse.Namespace, config: DeckConverterConfig) -> None:
    """
    Apply command-line overrides to the active deck converter configuration.

    Updates configuration values using any supported command-line
    arguments supplied by the user.

    Args:
        args: Parsed command-line arguments.
        config: Deck converter configuration to modify.
    """    
    # Stub pending implementation.
    pass

if __name__ == "__main__":
    main()