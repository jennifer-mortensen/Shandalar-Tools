"""
Card and edition data loaders for Shandalar Tools.

Provides functions for reading Forge edition files and Shandalar card
data from disk, including card names, edition codes, and the Shandalar
supported card list.
"""
from common import common_const, file_utils, path_utils
from config import runtime
from pathlib import Path
from typing import Iterable
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def get_edition_card_names(edition_name: str) -> Iterable[str]:
    """
    Yield card names from a Forge edition file.

    Reads the [cards] section of the edition file and parses each row
    into a card name, skipping any rows that cannot be parsed.

    Args:
        edition_name: The name of the edition to load.

    Raises:
        ValueError: If the edition name is empty.
    """    
    if not edition_name:
        raise ValueError("Edition name cannot be empty.") 
    
    file_path: Path = path_utils.build_edition_file_path(edition_name)

    edition_data = file_utils.read_text_section(
        file_path=file_path, 
        start_prefix=common_const.FORGE_CARDS_HEADER,
        end_prefixes=["["],
        skip_first_line=True,
        encoding_full_scan=runtime.get_encoding_scan_mode()
    )

    for row in edition_data:
        name = _parse_card_name_from_edition_row(row)
        if name:
            yield name

def get_scryfall_code(edition_name: str) -> str:
    """
    Read the Scryfall code from a Forge edition file.

    Args:
        edition_name: The name of the edition to look up.

    Raises:
        ValueError: If the edition name is empty or no Scryfall code is defined.
    """    
    if not edition_name:
        raise ValueError("Edition name cannot be empty.")

    file_path: Path = path_utils.build_edition_file_path(edition_name)

    try:
        line = next(file_utils.read_text_section(
            file_path=file_path,
            start_prefix=common_const.SCRYFALL_CODE_PREFIX,
            encoding_full_scan=runtime.get_encoding_scan_mode()
        ))
    except StopIteration:
        raise ValueError(f"Edition {edition_name} has no Scryfall code defined.")

    return line[len(common_const.SCRYFALL_CODE_PREFIX):]             

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
        column_number=common_const.SHANDALAR_DATA_FIELD_CARD_NAME,
        encoding_full_scan=runtime.get_encoding_scan_mode(True))
    )

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _parse_card_name_from_edition_row(row: str) -> str:
    """
    Parse a card name from a single row of a Forge edition file.

    Splits on the card delimiter and extracts the name starting from
    the expected column index. Returns an empty string if no name
    can be parsed, and logs a debug message in that case.

    Args:
        row: A single row string from the edition file.
    """    
    line: str = row.split(common_const.FORGE_EDITION_CARD_DELIMITER, 1)[0]
    card_name: str = " ".join(line.split()[common_const.EDITIONS_CARD_NAME_STARTING_COLUMN:])
    
    if not card_name:
        logger.debug("Could not parse card name from row: %s", line)

    return card_name 