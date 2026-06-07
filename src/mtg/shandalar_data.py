"""
Shandalar card data access and lookup utilities.

Provides helpers for loading the active Shandalar card pool and building
lookup structures used throughout the application.

Two lookup types are supported:

- Shandalar card ID lookup:
  Maps normalized Shandalar card IDs to ShandalarCard metadata.
  Used when resolving card IDs from Shandalar deck files.

- Shandalar card name lookup:
  Provides a sanitized set of card names for fast membership checks
  and validation of card names against the configured card pool.
"""
from common import common_utils, file_utils, path_utils, runtime
from mtg import shandalar_const
from mtg.shandalar_types import ShandalarCard
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_shandalar_card_id_lookup() -> dict[str, ShandalarCard]:
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

    logger.info("Building Shandalar card ID lookup...")

    card_lookup: dict[str, ShandalarCard] = {}
    file_path: Path = path_utils.build_shandalar_card_pool_path()

    for row in file_utils.read_csv_rows(file_path=file_path, encoding_full_scan=runtime.get_encoding_scan_mode()):
        card_id: str = normalize_shandalar_card_id(row[shandalar_const.SHANDALAR_DATA_FIELD_SHANDALAR_ID])
        if not looks_like_shandalar_card_id(card_id):
            continue
        card_lookup[card_id] = ShandalarCard(
            card_name=row[shandalar_const.SHANDALAR_DATA_FIELD_CARD_NAME],
            cost=row[shandalar_const.SHANDALAR_DATA_FIELD_COST],
            set=row[shandalar_const.SHANDALAR_DATA_FIELD_SET]
        )

    return card_lookup

def build_shandalar_card_name_lookup() -> set[str]:
    """
    Build a sanitized set of Shandalar card names for lookup.

    Reads the Shandalar card data file and returns a set of sanitized
    card names suitable for case-insensitive comparison.
    """    
    logger.info("Loading Shandalar card pool...")
    return common_utils.sanitize_set(get_shandalar_card_names())

def find_unsupported_in_shandalar(card_names: set[str], shandalar_card_name_lookup: set[str]) -> list[str]:
    """
    Identify cards that are not supported by Shandalar.

    Compares card names against the Shandalar lookup using sanitized
    comparison. Returns a list of unsupported card names in their
    original unsanitized form.

    Args:
        card_names: The set of card names to check.
        shandalar_card_name_lookup: A sanitized set of Shandalar supported card names.
    """    
    unsupported_card_names: list[str] = [c for c in card_names if common_utils.sanitize_string(c) not in shandalar_card_name_lookup]
    logger.info("Identified %d unsupported cards.", len(unsupported_card_names))
    
    return unsupported_card_names

def get_shandalar_card_names() -> set[str]:
    """
    Read all card names from the Shandalar card data file.

    Resolves the file path from the configured card pool name and data
    directory. Uses a full encoding scan by default due to the size of
    the file.
    """    
    file_path: Path = path_utils.build_shandalar_card_pool_path()
    return set(file_utils.read_csv_column(
        file_path=file_path,
        column_number=shandalar_const.SHANDALAR_DATA_FIELD_CARD_NAME,
        encoding_full_scan=runtime.get_encoding_scan_mode(True))
    )

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
        and common_utils.parse_int(field_value[len(shandalar_const.SHANDALAR_ID_PREFIX):]) is not None):
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

def validate_shandalar_card_id(card_id: str, shandalar_card_id_lookup: dict[str, ShandalarCard]) -> bool:
    """
    Validate a Shandalar card ID.

    Verifies that the ID exists in the canonical Shandalar card pool.

    Args:
        card_id: The card ID to validate.
        shandalar_card_id_lookup: Lookup table of canonical Shandalar card
            metadata keyed by normalized Shandalar card ID.        

    Returns:
        True if the card ID is valid, otherwise False.
    """    
    normalized_card_id: str = normalize_shandalar_card_id(card_id)

    if normalized_card_id not in shandalar_card_id_lookup:
        logger.warning(
            "Attempted to parse invalid Shandalar ID '%s' (normalized: '%s')",
            card_id,
            normalized_card_id
        )
        return False
    
    return True