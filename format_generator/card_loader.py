"""
Data loading and file parsing utilities.

Responsible for:
- Reading edition data and extracting card names and metadata
- Loading CSV-based configuration (editions, banned cards, Shandalar data)
- Handling text section extraction from Forge files
- Detecting file encodings and normalizing file names
- Providing sanitized, structured data to higher-level modules

Acts as the primary interface between raw file data and application logic.
"""
from common import common_const, file_utils
from pathlib import Path
from typing import Iterable
import logging

logger = logging.getLogger(__name__)

# ==============================
# HIGH LEVEL LOADERS
# ==============================

def get_edition_code(edition_name: str) -> str:
    """
    Retrieve the Scryfall code for a given edition.

    Args:
        edition_name: The name of the edition.

    Returns:
        The Scryfall code associated with the edition.

    Raises:
        ValueError: If the edition name is empty, malformed,
            or missing a Scryfall code.
    """     
    if not edition_name:
        raise ValueError("Edition name cannot be empty.")

    file_path = get_edition_file_path(edition_name)
    encoding = file_utils.detect_file_encoding(file_path)

    try:
        line = next(file_utils.read_text_section(file_path=file_path, encoding=encoding, start_prefix=common_const.SCRYFALL_CODE_PREFIX))
    except StopIteration:
        raise ValueError(f"Edition {edition_name} has no Scryfall code defined.")

    return line[len(common_const.SCRYFALL_CODE_PREFIX):] 

def get_edition_cards(edition_name: str) -> Iterable[str]:
    """
    Load all card names from a Forge edition file.

    Args:
        edition_name: The name of the edition.

    Returns:
        Card names generator from a Forge edition file.
    """    
    if not edition_name:
        raise ValueError("Edition name cannot be empty.") 
    
    file_path = get_edition_file_path(edition_name)
    encoding = file_utils.detect_file_encoding(file_path)

    edition_data = file_utils.read_text_section(
        file_path=file_path, encoding=encoding, 
        start_prefix=common_const.FORGE_CARDS_HEADER,
        end_prefixes=["["],
        skip_first_line=True
    )

    for row in edition_data:
        name = _parse_card_name_from_edition_row(row)
        if name:
            yield name

def get_edition_list(csv_file_path: Path) -> list[str]:
    """
    Load a list of edition names from a CSV configuration file.

    Args:
        csv_file_path: Path to the CSV file.

    Returns:
        A list of edition names.
    """    
    return list(file_utils.read_csv_column(csv_file_path, 0, skip_prefixes=[common_const.COMMENT_PREFIX]))

def get_shandalar_cards() -> set[str]:
    """
    Load the set of cards supported by Shandalar.

    Returns:
        A set of supported card names.
    """    
    cards = file_utils.read_csv_column(file_path=common_const.FILE_SHANDALAR_CSV, column_number=common_const.SHANDALAR_CARD_NAME_STARTING_COLUMN, encoding_full_scan=True)
    return set(cards)

def get_user_banned_cards(file_path: Path) -> list[str]:
    """
    Load user-defined banned cards from a CSV file.

    Args:
        file_path: Path to the user-banned cards file.

    Returns:
        A list of banned card names.
    """    
    return list(file_utils.read_csv_column(file_path=file_path, column_number=0, skip_prefixes=[common_const.COMMENT_PREFIX]))

# ==============================
# PUBLIC HELPERS
# ==============================

def ensure_extension(file_path: Path, extension: str) -> Path:
    """
    Ensure the path has the given extension if one is not 
    already present.

    Args:
        file_path: The file path to normalize.
        extension: The required file extension.

    Returns:
        A Path object with the correct extension.
    """    
    return file_path if file_path.suffix else file_path.with_suffix(f".{extension}")

def get_edition_file_path(edition_name: str) -> Path:
    """
    Construct the file path for a Forge edition file.

    Args:
        edition_name: The name of the edition.

    Returns:
        The full path to the edition file.

    Raises:
        ValueError: If the edition name is empty.
    """    
    if not edition_name:
        raise ValueError(f"Edition name cannot be empty.")

    return common_const.EDITIONS_DIR / f"{edition_name}{common_const.EDITION_FILE_SUFFIX}"

def sanitize_name(name: str) -> str:
    """
    Normalize a name by trimming whitespace and converting to lowercase.

    Args:
        name: The string to sanitize.

    Returns:
        A sanitized string.
    """    
    return name.strip().lower()

def sanitize_card_set(cards: set[str]) -> set[str]:
    """
    Sanitize a set of card names.

    Args:
        cards: A set of card names.

    Returns:
        A sanitized set with lowercase, trimmed names.
    """    
    return {sanitize_name(c) for c in cards}

# ==============================
# PRIVATE HELPERS
# ==============================

def _parse_card_name_from_edition_row(row: str) -> str:
    """
    Extract a card name from a Forge edition data row.

    Args:
        row: A line from a Forge edition file.

    Returns:
        The parsed card name.
    """    
    line = row.split(common_const.FORGE_EDITION_CARD_DELIMITER, 1)[0]
    card_name = " ".join(line.split()[common_const.EDITIONS_CARD_NAME_STARTING_COLUMN:])
    
    if not card_name:
        logger.debug("Could not parse card name from row: %s", line)

    return card_name 