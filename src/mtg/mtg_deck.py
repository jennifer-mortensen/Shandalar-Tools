"""
Format-agnostic deck utilities for Shandalar Tools.

Provides shared deck operations used across supported deck formats,
including deck loading and format detection. Acts as the entry point
for deck-level logic that is not specific to either Forge or
Shandalar deck formats.
"""
from common import file_utils, path_utils
from mtg import forge_deck
from mtg.mtg_types import DeckType
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def get_deck_type(raw_deck: str) -> DeckType:
    """
    Determine the detected deck format from a raw deck file.

    Attempts to identify the deck format using known format signatures.
    If the file does not match the Forge deck format, the deck is assumed
    to be a Shandalar deck.

    Args:
        raw_deck: The full raw contents of the deck file.

    Returns:
        The detected deck format type.
    """    
    logger.info("Determining deck format...")

    if forge_deck.is_forge_deck(raw_deck):
        logger.info("Deck file appears to be of Forge format.")
        return DeckType.FORGE
    
    logger.info("Deck file does not appear to be of Forge format. Defaulting to Shandalar format.")
    return DeckType.SHANDALAR

def load_raw_deck(deck_name: str) -> str:
    """
    Load and return the raw contents of a deck file.

    Resolves the deck path within the configured input deck directory,
    automatically applies the default deck file extension if missing,
    and reads the full file contents using automatic encoding detection.

    Args:
        deck_name: The name of the deck file, with or without extension.

    Returns:
        The full raw contents of the deck file as a string.

    Raises:
        OSError: If the deck file cannot be opened or read.
    """  
    file_path: Path = path_utils.build_input_deck_file_path(deck_name)
    logger.info("Loading '%s'...", file_path)         
    return file_utils.load_raw_file(file_path)