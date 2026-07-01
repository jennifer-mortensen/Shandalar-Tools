"""
Shandalar deck parsing and writing utilities.

Provides helpers for parsing, validating, and writing
Shandalar deck files, including deck titles, sideboard
sections, and card entries.
"""
from common import paths, parse_utils, string_utils
from mtg import shandalar_const, shandalar_data
from mtg.mtg_types import Card, Color, Deck, DeckType
from mtg.shandalar_types import ShandalarCardFields
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_deck_from_shandalar(raw_deck: str) -> Deck:
    """
    Build a normalized deck object from a Shandalar deck file.

    Args:
        raw_deck: The raw contents of the Shandalar deck file.

    Returns:
        A normalized deck object.
    """ 
    logger.info("Building deck from Shandalar format...")   

    deck: Deck = Deck(type=DeckType.SHANDALAR)
    current_deck_section: list[Card] = deck.cards

    for line_number, line in enumerate(raw_deck.splitlines(), start=1):
        line = line.strip()
        if line == "":
            continue

        sideboard_color: Color | None = get_sideboard_color(line)
        if sideboard_color is not None:
            current_deck_section = deck.color_sideboards[sideboard_color].cards
            continue

        card: Card | None = parse_shandalar_deck_card(line)
        if not card:
            if line_number == shandalar_const.SHANDALAR_DECK_TITLE_LINE:
                deck.name = parse_shandalar_deck_title(line)
            else:
                logger.warning("Unable to parse card at line %d: '%s'", line_number, line)
            continue

        current_deck_section.append(card)

    return deck

def get_sideboard_color(raw_line: str) -> Color | None:
    """
    Return the sideboard color represented by a Shandalar sideboard header.

    Parses a raw deck line and attempts to identify a Shandalar sideboard
    section header such as '.vBlack' or '.vNone'.

    Args:
        raw_line: A raw line from a Shandalar deck file.

    Returns:
        The associated sideboard color if the line is a valid sideboard
        header, otherwise None.
    """    
    sanitized_line: str = string_utils.sanitize_string(raw_line)

    if not sanitized_line:
        return None
    
    return shandalar_const.SHANDALAR_SIDEBOARD_HEADER.get(sanitized_line.split()[0]) # ignore text after whitespace

def parse_shandalar_deck_card(raw_line: str) -> Card | None:
    """
    Parse a raw Shandalar card line into a normalized Card object.

    Attempts to parse a raw deck line as a valid Shandalar card
    entry. If the line does not represent a valid card record,
    returns None.

    Args:
        raw_line: A raw line from a Shandalar deck file.

    Returns:
        A parsed Card object if successful, otherwise None.
    """
    card_fields: ShandalarCardFields | None  = _parse_shandalar_card_fields(raw_line)
    
    if card_fields is None:
        return None
    
    return Card(
        quantity=card_fields[shandalar_const.SHANDALAR_CARD_FIELD_QUANTITY],
        shandalar_id=card_fields[shandalar_const.SHANDALAR_CARD_FIELD_ID],
        name=card_fields[shandalar_const.SHANDALAR_CARD_FIELD_NAME]
    )

def parse_shandalar_deck_title(line: str) -> str:
    """
    Parse a Shandalar deck title line.

    Extracts the deck name from a Shandalar deck title line by removing
    any trailing metadata beginning with the title delimiter.

    Examples:
        "Lord of Fate (Bl/Wh, 4th Edition)" -> "Lord of Fate"
        "Lord of Fate" -> "Lord of Fate"

    Args:
        line: The raw title line from a Shandalar deck file.

    Returns:
        The parsed deck title with surrounding whitespace removed.
    """    
    return line.split(shandalar_const.SHANDALAR_DECK_TITLE_DELIMITER, maxsplit=1)[0].strip()

def write_shandalar_deck(deck: Deck, file_name: str) -> None:
    """
    Write a deck in Shandalar deck format.

    Args:
        deck: The deck to write.
        file_name: Name of the written deck file.
    """
    file_path: Path = paths.build_output_deck_file_path(deck_name=file_name, deck_type=DeckType.SHANDALAR)    
    logger.info("Writing Shandalar deck to %s...", file_path)            

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _parse_shandalar_card_fields(raw_line: str) -> ShandalarCardFields | None:
    """
    Parse a raw Shandalar card line into normalized card fields.

    Splits a raw deck line into its component card fields,
    validates the card ID and quantity, and reconstructs the
    card name as a single field, preserving spaces in multi-word
    names.

    Args:
        raw_line: A raw card line from a Shandalar deck file.

    Returns:
        A tuple containing the normalized card ID, quantity,
        and card name, or None if the line does not represent
        a valid Shandalar card entry.
    """
    raw_fields: list[str] = raw_line.strip().split()

    # Ensure sufficient fields
    if len(raw_fields) < shandalar_const.SHANDALAR_CARD_MINIMUM_FIELDS:
        logger.debug(
            "Ignoring Shandalar card line with insufficient fields (count: %d, minimum: %d): '%s'",
            len(raw_fields),
            shandalar_const.SHANDALAR_CARD_MINIMUM_FIELDS,
            raw_line
        )
        return None    

    # Parse card ID
    card_id: str = raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_ID] 
    if not shandalar_data.looks_like_shandalar_card_id(card_id):
        return None
    if not shandalar_data.validate_shandalar_card_id(card_id):
        logger.warning(
            "Attempted to parse invalid Shandalar ID '%s' (normalized: '%s')",
            card_id,
            shandalar_data.normalize_shandalar_card_id(card_id)
        )        
        return None
    
    # Parse card quantity
    if not _validate_shandalar_card_quantity(quantity_field=raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_QUANTITY], raw_line=raw_line):
        return None 
    quantity: int = int(raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_QUANTITY]) # assign after validation to avoid conversion value error
    
    # Parse card name
    contains_name: bool = len(raw_fields) > shandalar_const.SHANDALAR_CARD_FIELD_NAME # offset by 1 due to list index 0
    name: str = " ".join(raw_fields[shandalar_const.SHANDALAR_CARD_FIELD_NAME:]) if contains_name else ""

    return (card_id, quantity, name)

def _validate_shandalar_card_quantity(quantity_field: str, raw_line: str) -> bool:
    """
    Validate a Shandalar card quantity field.

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
            "Shandalar card line has invalid quantity field ('%s'): '%s'",
            quantity_field,
            raw_line
        )
        return False   
    if quantity < shandalar_const.SHANDALAR_CARD_MINIMUM_QUANTITY:
        logger.warning(
            "Shandalar card line has insufficient quantity (quantity: %d, minimum: %d): '%s'",
            quantity,
            shandalar_const.SHANDALAR_CARD_MINIMUM_QUANTITY,
            raw_line
        )
        return False

    return True  