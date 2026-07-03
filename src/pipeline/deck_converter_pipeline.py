"""
Pipeline functions for the Shandalar Tools deck converter.

Orchestrates deck conversion workflows, including deck loading,
format detection, parsing, translation, and output generation.
"""
from mtg import forge_deck, mtg_deck, shandalar_deck
from mtg.mtg_types import Deck, DeckType
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATA CLASS CONSTRUCTORS
# ==============================
def build_deck(deck_name: str) -> Deck:
    """
    Build and return a normalized deck object from a deck file.

    Loads the raw deck file, detects its source format, and dispatches
    to the appropriate format-specific deck builder.

    Args:
        deck_name: The name of the deck file to load.

    Returns:
        A normalized deck object.
    """
    logger.info("Preparing to build deck '%s'...", deck_name)    
    raw_deck: str = mtg_deck.load_raw_deck(deck_name)
    deck_type: DeckType = mtg_deck.get_deck_type(raw_deck)

    if deck_type is DeckType.FORGE:
        return forge_deck.build_deck_from_forge(raw_deck)
    if deck_type is DeckType.SHANDALAR:
        return shandalar_deck.build_deck_from_shandalar(raw_deck)
    
    raise AssertionError(f"Unhandled deck type: {deck_type}")

# ==============================
# HIGH LEVEL FUNCTIONS
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

def write_translated_deck(deck: Deck, file_name: str) -> None:
    """
    Write a deck to disk using its translated deck format.

    Dispatches to the appropriate format-specific deck writer based on
    the deck's stored deck type.

    Args:
        deck: The deck to write.
        file_name: Name of the written deck file.
    """
    translated_type = deck.type.inverse()    
    if translated_type is DeckType.FORGE:
        forge_deck.write_forge_deck(deck=deck, file_name=file_name)
    else:
        shandalar_deck.write_shandalar_deck(deck=deck, file_name=file_name)