"""
MTG: Forge deck utilities for Shandalar Tools.

Will provide functions for reading, validating, transforming, and
writing MTG: Forge deck data. Currently a stub pending full
implementation.
"""
from deck_translator.translator_const import FORGE_DECK_HEADER

def is_forge_deck(raw_deck: str) -> bool:
    """
    Determine whether a raw deck file appears to be an MTG: Forge deck.

    Checks for the presence of the expected Forge deck header within the
    raw file contents.

    Args:
        raw_deck: The full raw contents of the deck file.

    Returns:
        True if the file appears to match the Forge deck format,
        otherwise False.
    """    
    return FORGE_DECK_HEADER in raw_deck