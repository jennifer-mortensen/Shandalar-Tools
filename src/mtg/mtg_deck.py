"""
Format-agnostic deck utilities for Shandalar Tools.

Provides shared deck operations used across supported deck formats,
including deck loading and format detection. Acts as the entry point
for deck-level logic that is not specific to either Forge or
Shandalar deck formats.
"""
from common import file_utils, parse_utils, paths
from mtg import mtg_const
from mtg.mtg_types import Card, Color, Deck
from pathlib import Path
from resources import lookup_loader
from resources.shandalar_card_lookup import ShandalarCardLookup
from mtg.shandalar_types import ShandalarCard
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
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
    file_path: Path = paths.build_input_deck_file_path(deck_name)
    logger.info("Loading '%s'...", file_path)         
    return file_utils.load_raw_file(file_path)

def update_deck_colors(deck: Deck, card: Card, dataset: str | None = None) -> None:
    """
    Update a deck's color identity using a card.

    Resolves the corresponding Shandalar card metadata and adds
    any colors represented by the card's casting cost to the
    deck's color identity.

    Args:
        deck: The deck to update.
        card: The card whose colors should be added.
        dataset: The Shandalar dataset used to resolve card
            metadata.

    Raises:
        ValueError: If the card cannot be resolved from the
            specified dataset.
    """    
    lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)
    shandalar_card: ShandalarCard = lookup.get(card.shandalar_id)

    if not shandalar_card:
        raise ValueError(f"Could not find card with id '{card.shandalar_id}' in dataset '{lookup.dataset}'.")
    colors: set[Color] = shandalar_card.get_colors()
    for color in colors:
        deck.colors.add(color)

def validate_card_quantity(quantity_field: str, raw_line: str) -> bool:
    """
    Validate acard quantity field.

    Verifies that the quantity field can be parsed as an integer and
    meets the minimum allowed card quantity.

    Args:
        quantity_field: The quantity field to validate.
        raw_line: The source line being validated, used for logging.

    Returns:
        True if the quantity field is valid, otherwise False.
    """   
    quantity: int | None = parse_utils.parse_int(quantity_field)
   
    if quantity is None:
        logger.warning(
            "Card line has invalid quantity field ('%s'): '%s'",
            quantity_field,
            raw_line
        )
        return False   
    if quantity < mtg_const.CARD_MINIMUM_QUANTITY:
        logger.warning(
            "Card line has insufficient quantity (quantity: %d, minimum: %d): '%s'",
            quantity,
            mtg_const.CARD_MINIMUM_QUANTITY,
            raw_line
        )
        return False

    return True  