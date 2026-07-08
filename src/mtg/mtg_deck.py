"""
Format-agnostic deck utilities for Shandalar Tools.

Provides shared deck operations used across supported deck formats,
including deck loading and format detection. Acts as the entry point
for deck-level logic that is not specific to either Forge or
Shandalar deck formats.
"""
from common import parse_utils
from mtg import mtg_const
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
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