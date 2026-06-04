"""
Shandalar deck utilities for Shandalar Tools.

Will provide functions for reading, validating, transforming, and
writing Shandalar deck data. Currently a stub pending full
implementation.
"""
from common import common_const, common_utils, file_utils, path_utils
from config import runtime
from deck_translator.translator_common import Card, Color, ShandalarCard, ShandalarCardFields, SHANDALAR_SIDEBOARD_HEADER
from deck_translator import translator_common
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_shandalar_card_lookup() -> dict[str, ShandalarCard]:
    """
    Build a lookup table of canonical Shandalar card metadata.

    Reads the configured Shandalar card pool data file and constructs a
    dictionary keyed by Shandalar card ID for fast metadata lookup during
    deck parsing, validation, and translation.

    Returns:
        A dictionary mapping Shandalar card IDs to ShandalarCard metadata.
    """
    # TODO for v2.1+: Cache the lookup table after first build and reuse it
    # when the source dataset has not changed.

    card_lookup: dict[str, ShandalarCard] = {}
    file_path: Path = path_utils.build_shandalar_card_pool_path()

    for row in file_utils.read_csv_rows(file_path=file_path, encoding_full_scan=runtime.get_encoding_scan_mode()):
        card_id: str = normalize_shandalar_card_id(row[common_const.SHANDALAR_DATA_FIELD_SHANDALAR_ID])
        if not _looks_like_shandalar_card_id(card_id):
            continue
        card_lookup[card_id] = ShandalarCard(
            card_name=row[common_const.SHANDALAR_DATA_FIELD_CARD_NAME],
            cost=row[common_const.SHANDALAR_DATA_FIELD_COST],
            set=row[common_const.SHANDALAR_DATA_FIELD_SET]
        )

    return card_lookup

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
    sanitized_line: str = common_utils.sanitize_string(raw_line)

    if not sanitized_line:
        return None
    
    return SHANDALAR_SIDEBOARD_HEADER.get(sanitized_line.split()[0]) # ignore text after whitespace

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

def parse_shandalar_card(raw_line: str, shandalar_card_lookup: dict[str, ShandalarCard]) -> Card | None:
    """
    Parse a raw Shandalar card line into a normalized Card object.

    Attempts to parse a raw deck line as a valid Shandalar card entry. If
    the line does not represent a parsable card record, returns None.

    Args:
        raw_line: A raw line from a Shandalar deck file.
        shandalar_card_lookup: Lookup table of canonical Shandalar card
            metadata keyed by normalized Shandalar card ID.        

    Returns:
        A parsed Card object if successful, otherwise None.
    """    
    card_fields: ShandalarCardFields | None  = _parse_shandalar_card_fields(
        raw_line=raw_line,
        shandalar_card_lookup=shandalar_card_lookup
    )
    
    if card_fields is None:
        return None
    
    return Card(
        copies=card_fields[translator_common.SHANDALAR_CARD_FIELD_QUANTITY],
        shandalar_id=card_fields[translator_common.SHANDALAR_CARD_FIELD_ID],
        name=card_fields[translator_common.SHANDALAR_CARD_FIELD_NAME]
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
    return line.split(translator_common.SHANDALAR_DECK_TITLE_DELIMITER, maxsplit=1)[0].strip()

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _parse_shandalar_card_fields(raw_line: str, shandalar_card_lookup: dict[str, ShandalarCard]) -> ShandalarCardFields | None:
    """
    Parse a raw Shandalar card line into normalized card fields.

    Splits a raw deck line into its component card fields and reconstructs
    the card name as a single field, preserving spaces in multi-word names.

    Args:
        raw_line: A raw card line from a Shandalar deck file.
        shandalar_card_lookup: Lookup table of canonical Shandalar card
            metadata keyed by normalized Shandalar card ID.

    Returns:
        A tuple containing the normalized card ID, quantity, and card name,
        or None if the line does not represent a valid Shandalar card entry.
    """    
    raw_fields: list[str] = raw_line.strip().split()

    # Ensure sufficient fields
    if len(raw_fields) < translator_common.SHANDALAR_CARD_MINIMUM_FIELDS:
        logger.debug(
            "Ignoring Shandalar card line with insufficient fields (count: %d, minimum: %d): '%s'",
            len(raw_fields),
            translator_common.SHANDALAR_CARD_MINIMUM_FIELDS,
            raw_line
        )
        return None    

    # Parse card ID
    card_id: str = raw_fields[translator_common.SHANDALAR_CARD_FIELD_ID] 
    if not _validate_shandalar_card_id(card_id=card_id, raw_line=raw_line, shandalar_card_lookup=shandalar_card_lookup):
        return None
    
    # Parse card quantity
    if not _validate_shandalar_card_quantity(quantity_field=raw_fields[translator_common.SHANDALAR_CARD_FIELD_QUANTITY], raw_line=raw_line):
        return None 
    quantity: int = int(raw_fields[translator_common.SHANDALAR_CARD_FIELD_QUANTITY]) # assign after validation to evade conversion value error
    
    # Parse card name
    contains_name: bool = len(raw_fields) > translator_common.SHANDALAR_CARD_FIELD_NAME # offset by 1 due to list index 0
    name: str = " ".join(raw_fields[translator_common.SHANDALAR_CARD_FIELD_NAME:]) if contains_name else ""

    return (card_id, quantity, name)

def _looks_like_shandalar_card_id(field_value: str) -> bool:
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
    
    return (
        field_value.startswith(translator_common.SHANDALAR_ID_PREFIX) 
        and common_utils.parse_int(field_value[len(translator_common.SHANDALAR_ID_PREFIX):]) is not None
    )

def _validate_shandalar_card_id(card_id: str, raw_line: str, shandalar_card_lookup: dict[str, ShandalarCard]) -> bool:
    """
    Validate a Shandalar card ID.

    Verifies that the ID matches the expected Shandalar ID format and
    exists in the canonical Shandalar card pool.

    Args:
        card_id: The card ID to validate.
        raw_line: The source line being validated, used for logging.
        shandalar_card_lookup: Lookup table of canonical Shandalar card
            metadata keyed by normalized Shandalar card ID.        

    Returns:
        True if the card ID is valid, otherwise False.
    """    
    if not _looks_like_shandalar_card_id(card_id):
        logger.debug("Shandalar card line lacks Shandalar ID signature: '%s'", raw_line)
        return False

    if card_id not in shandalar_card_lookup:
       logger.warning("Shandalar card line has invalid ID (ID: '%s'): '%s'", card_id, raw_line)
       return False
    
    return True

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
    quantity: int | None = common_utils.parse_int(quantity_field)
   
    if quantity is None:
        logger.warning(
            "Shandalar card line has invalid quantity field ('%s'): '%s'",
            quantity_field,
            raw_line
        )
        return False   
    if quantity < translator_common.SHANDALAR_CARD_MINIMUM_QUANTITY:
        logger.warning(
            "Shandalar card line has insufficient quantity (quantity: %d, minimum: %d): '%s'",
            quantity,
            translator_common.SHANDALAR_CARD_MINIMUM_QUANTITY,
            raw_line
        )
        return False       

    return True  
