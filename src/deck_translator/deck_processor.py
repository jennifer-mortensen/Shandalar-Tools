"""
Deck processing and translation utilities for Shandalar Tools.

Will provide shared deck processing logic used across multiple deck
formats, including format detection, translation routing, validation,
and cross-format transformations. Currently a stub pending full
implementation.
"""
from common import common_const, file_utils
from deck_translator import forge_deck, translator_const
from deck_translator.translator_const import DeckType
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

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
    file_path = build_input_deck_file_path(deck_name)
    logger.info("Loading '%s'...", file_path)         
    return file_utils.load_raw_file(file_path)

def build_input_deck_file_path(deck_name: str) -> Path:
    """
    Build the normalized path for an input deck file.

    Resolves the deck path within the configured input deck directory and
    automatically applies the default deck file extension if missing.

    Args:
        deck_name: The name of the deck file, with or without extension.

    Returns:
        The normalized input deck file path.
    """    
    return file_utils.ensure_extension(file_path=common_const.INPUT_DECK_DIR / deck_name, extension=translator_const.FILE_TYPE_DECK)

def build_output_deck_file_path(deck_name: str, deck_type: DeckType) -> Path:
    """
    Build the normalized path for an output deck file.

    Selects the appropriate output directory based on the target deck type
    and automatically applies the default deck file extension if missing.

    Args:
        deck_name: The name of the deck file, with or without extension.
        deck_type: The target deck format type.

    Returns:
        The normalized output deck file path.
    """    
    output_dir = common_const.OUTPUT_FORGE_DECK_DIR if deck_type is DeckType.FORGE else common_const.OUTPUT_SHANDALAR_DECK_DIR
    return file_utils.ensure_extension(file_path=output_dir / deck_name, extension=translator_const.FILE_TYPE_DECK)