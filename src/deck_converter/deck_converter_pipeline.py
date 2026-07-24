"""
Pipeline functions for the Shandalar Tools deck converter.

Orchestrates deck conversion workflows, including deck loading,
format detection, parsing, translation, and output generation.
"""
from common import file_utils, paths, settings
from mtg import forge_deck, shandalar_deck
from mtg.deck import Deck, DeckType
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def run_pipeline() -> None:
    """
    Execute the deck conversion pipeline.

    Loads the configured input deck, detects its format,
    converts it to the opposite supported format, and writes
    the translated deck to the configured output location.
    """    
    _write_translated_deck(_build_deck())

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _build_deck() -> Deck:
    """
    Build and return a normalized deck object from a deck file.

    Resolves the input deck file path, loads the deck contents,
    detects the source deck format, and dispatches to the
    appropriate format-specific deck builder.

    Returns:
        A normalized deck object.

    Raises:
        AssertionError: If the detected deck type is not
            supported.
    """
    deck_name: str = settings.get_input_deck_file_name()

    logger.info("Preparing to build deck '%s'...", deck_name) 

    file_path: Path = paths.build_input_deck_file_path(deck_name)
    raw_deck: str = file_utils.load_raw_file(file_path)
    deck_type: DeckType = _get_deck_type(raw_deck)

    if deck_type is DeckType.FORGE:
        return forge_deck.build_deck_from_forge(raw_deck=raw_deck, deck_path=file_path)
    if deck_type is DeckType.SHANDALAR:
        return shandalar_deck.build_deck_from_shandalar(raw_deck)
    
    raise AssertionError(f"Unhandled deck type: {deck_type}")

def _get_deck_type(raw_deck: str) -> DeckType:
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

def _write_translated_deck(deck: Deck) -> None:
    """
    Write a deck to disk using its translated deck format.

    Dispatches to the appropriate format-specific deck writer based on
    the deck's stored deck type.

    Args:
        deck: The deck to write.
    """
    translated_type = deck.type.inverse()    
    if translated_type is DeckType.FORGE:
        forge_deck.write_forge_deck(deck=deck, file_name=settings.get_output_forge_deck_file_name())
    else:
        shandalar_deck.write_shandalar_deck(deck=deck, file_name=settings.get_output_shandalar_deck_file_name())