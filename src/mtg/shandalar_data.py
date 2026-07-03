"""
Shandalar card data utilities.

Provides helpers for working with the active Shandalar card
lookup, including card ID validation, card name validation,
and Shandalar-specific normalization utilities.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from common import string_utils, parse_utils
from mtg import shandalar_const
from resources import lookup_loader
import logging

if TYPE_CHECKING:
    from resources.shandalar_card_lookup import ShandalarCardLookup

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def find_unsupported_in_shandalar(card_names: set[str], dataset: str | None = None) -> list[str]:
    """
    Identify cards that are not supported by Shandalar.

    Compares the supplied card names against the Shandalar card
    lookup for the specified dataset using normalized name
    comparison. Unsupported cards are returned in their original,
    unmodified form.

    Args:
        card_names: The set of card names to check.
        dataset: Optional dataset whose card lookup should be
            used. If omitted, the default dataset is used.

    Returns:
        A list of unsupported card names.
    """   
    lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)
    unsupported_card_names: list[str] = [c for c in card_names if string_utils.normalize_string(c) not in lookup.names_normalized]
    logger.info("Identified %d unsupported cards.", len(unsupported_card_names))
    
    return unsupported_card_names

def looks_like_shandalar_card_id(field_value: str) -> bool:
    """
    Determine whether a value resembles a Shandalar card ID.

    Performs a lightweight structural check by verifying that the value
    begins with the expected Shandalar ID prefix and that the remaining
    characters can be parsed as an integer.

    Args:
        field_value: The value to test.

    Returns:
        True if the value resembles a Shandalar card ID, otherwise False.
    """    
    field_value = normalize_shandalar_card_id(field_value)

    if (field_value.startswith(shandalar_const.SHANDALAR_ID_PREFIX)
        and parse_utils.parse_int(field_value[len(shandalar_const.SHANDALAR_ID_PREFIX):]) is not None):
          return True

    logger.debug("Shandalar card ID field lacks valid ID signature: '%s'", field_value)
    return False

def normalize_shandalar_card_id(card_id: str) -> str:
    """
    Normalize a Shandalar card ID.

    Removes leading zeros, which are ignored by Shandalar when
    interpreting card IDs.

    Args:
        card_id: The card ID to normalize.

    Returns:
        The normalized card ID.
    """    
    return card_id.lstrip("0")

def validate_shandalar_card_id(card_id: str, dataset: str | None = None) -> bool:
    """
    Validate a Shandalar card ID.

    Verifies that the supplied card ID exists in the Shandalar
    card lookup for the specified dataset.

    Args:
        card_id: The card ID to validate.
        dataset: Optional dataset whose card lookup should be
            used. If omitted, the default dataset is used.

    Returns:
        True if the card ID is valid, otherwise False.
    """
    normalized_card_id: str = normalize_shandalar_card_id(card_id)
    lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)    

    return normalized_card_id in lookup