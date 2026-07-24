"""
Constants for the Shandalar Tools deck converter.

Defines command-line metadata, logging identifiers, and other
tool-specific constants used by the deck converter CLI and pipeline.
"""
from common import args_types
from common.args_types import CliDefinition
# ==============================
# CLI CONSTANTS
# ==============================
MODULE_NAME: str = "deck_converter"
LOG_NAME: str = MODULE_NAME

CLI_DEFINITION: CliDefinition = CliDefinition(
    prog="deck-converter",
    description="Convert decks between Shandalar and Forge formats.",
    epilog=(
        "Examples:\n"
        "  %(prog)s\n"
        "  %(prog)s -i my_deck\n"
        "  %(prog)s -o converted_deck\n"
        "  %(prog)s -s full"
    ),
    arguments = (
        # Common
        args_types.ARGUMENT_ENCODING_SCAN_MODE,
        args_types.ARGUMENT_LOG_FILE_NAME,
        args_types.ARGUMENT_LOG_OVERWRITE,
        args_types.ARGUMENT_LOG_PREVIEW_LIMIT,
        args_types.ARGUMENT_SHANDALAR_DATASET,
        # Deck Converter
        args_types.ARGUMENT_INPUT_DECK,
        args_types.ARGUMENT_OUTPUT_DECK
    )    
)
