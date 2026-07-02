"""
Forge deck parsing and serialization for Shandalar Tools.

Provides helpers for detecting, reading, and writing Forge deck
files and converting them to and from the shared Deck model.
"""
from common import file_utils, paths, string_utils
from mtg import forge_const
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
    deck.name = parse_deck_name(raw_deck)
    in_main: bool = False

    for line_number, line in enumerate(raw_deck.splitlines(), start=1):
        line = line.strip()
        
        if not in_main:
            if string_utils.sanitized_starts_with(text=line, prefix=forge_const.FORGE_DECK_MAIN_HEADER):
                in_main = True
            continue
        if file_utils.is_section_header(line):
            break

        # Parse Cards

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
    return forge_const.FORGE_DECK_MAIN_HEADER in raw_deck

def parse_deck_name(raw_deck: str) -> str:
    """
    Parse the name of a Forge deck.

    Extracts the value of the Forge deck name field from the
    supplied raw deck contents.

    Args:
        raw_deck: The raw Forge deck contents.

    Returns:
        The deck name if present; otherwise "".
    """
    deck_name: str | None = string_utils.extract_text_field(text=raw_deck, field_name=forge_const.FORGE_DECK_NAME_PREFIX) 
    return deck_name if deck_name is not None else ""

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

