"""
Constants for the Shandalar Tools deck converter.

Defines command-line metadata, logging identifiers, and other
tool-specific constants used by the deck converter CLI and pipeline.
"""

# ==============================
# CLI CONSTANTS
# ==============================
MODULE_NAME: str = "deck_converter"
LOG_NAME: str = MODULE_NAME
CLI_PROG: str = "deck-converter"
CLI_DESCRIPTION: str = "Convert decks between Shandalar and Forge formats."
CLI_EPILOG: str = "Examples:\n  %(prog)s\n  %(prog)s -s full"