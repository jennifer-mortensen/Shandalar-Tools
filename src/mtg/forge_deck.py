"""
Forge deck parsing and serialization for Shandalar Tools.

Provides helpers for detecting, reading, and writing Forge deck
files and converting them to and from the shared Deck model.
"""
from common import paths
from mtg.forge_const import FORGE_DECK_MAIN_HEADER
from mtg.mtg_types import Deck, DeckType
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_deck_from_forge(raw_deck: str) -> Deck:
    """
    Build a normalized deck object from a Forge deck file.

    Parses the raw Forge deck contents and converts them into the
    shared Deck representation.

    Args:
        raw_deck: The raw contents of the Forge deck file.

    Returns:
        A normalized deck object.
    """
    logger.info("Building deck from Forge format...")    
    deck: Deck = Deck(type=DeckType.FORGE)

    for line_number, line in enumerate(raw_deck.splitlines(), start=1):
        pass

    return deck

def is_forge_deck(raw_deck: str) -> bool:
    """
    Determine whether a raw deck file appears to be a Forge deck.

    Checks for the presence of the expected Forge deck header within the
    raw file contents.

    Args:
        raw_deck: The full raw contents of the deck file.

    Returns:
        True if the file appears to match the Forge deck format,
        otherwise False.
    """    
    return FORGE_DECK_MAIN_HEADER in raw_deck

def write_forge_deck(deck: Deck, file_name: str) -> None:
    """
    Write a deck in Forge deck format.

    Serializes the supplied deck and writes it to the configured
    Forge output directory.

    Args:
        deck: The deck to write.
        file_name: Name of the deck file to write.
    """
    file_path: Path = paths.build_output_deck_file_path(deck_name=file_name, deck_type=DeckType.FORGE)
    logger.info("Writing Forge deck to %s...", file_path)    