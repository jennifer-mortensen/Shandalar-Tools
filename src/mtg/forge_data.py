"""
Forge edition data access and parsing utilities.

Provides helpers for reading Forge edition files, extracting
card names, and retrieving edition metadata such as edition
codes.
"""
from collections.abc import Iterable
from common import file_utils, paths, settings, string_utils
from mtg import forge_const
from pathlib import Path
from resources import data_map_loader
from resources.data_map import DataMap
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_format_card_pool(edition_names: list[str]) -> set[str]:
    """
    Build a set of card names from the specified Forge editions.

    Loads each edition in order, skipping duplicates. Logs a warning
    for any duplicate edition names detected.

    Args:
        edition_names: Names of the editions to load.

    Returns:
        A set containing all card names found across the supplied
        editions.
    """
    logger.info("Building card pool from editions...")    
    editions_loaded: set[str] = set()
    cards: set[str] = set()

    for edition in edition_names:
        sanitized_edition_name: str = string_utils.sanitize_string(edition)
        if sanitized_edition_name in editions_loaded:
            logger.warning("Duplicate edition '%s' detected; skipping.", edition)
            continue

        logger.debug("Loading edition '%s'...", edition)

        cards.update(get_edition_card_names(edition))
        editions_loaded.add(sanitized_edition_name)

    return cards

def collect_edition_codes(edition_names: list[str]) -> set[str]:
    """
    Collect edition codes for a list of edition names.

    Args:
        edition_names: Names of the editions to collect codes for.

    Returns:
        A set containing the edition codes for the supplied editions.
    """
    logger.info("Generating edition codes...")
    
    edition_codes: set[str] = set()

    for edition in edition_names:
        logger.debug("Collecting edition code for '%s'...", edition)
        code = get_edition_code(edition)
        edition_codes.add(code)

    return edition_codes

def edition_exists(edition_name: str) -> bool:
    """
    Determine whether a Forge edition exists.

    Checks for the presence of a Forge edition data file matching
    the supplied edition name.

    Args:
        edition_name: The edition name to check.

    Returns:
        True if the edition exists; otherwise False.
    """    
    return paths.build_edition_file_path(edition_name).exists()

def get_edition_card_names(edition_name: str) -> Iterable[str]:
    """
    Yield card names from a Forge edition file.

    Reads the [cards] section of the edition file and parses each row
    into a card name, skipping any rows that cannot be parsed.

    Args:
        edition_name: The name of the edition to load.

    Yields:
        Card names defined in the edition file.
    """  
    file_path: Path = paths.build_edition_file_path(edition_name)

    edition_data = file_utils.read_text_section(
        file_path=file_path, 
        start_prefix=forge_const.FORGE_EDITION_CARDS_HEADER,
        end_prefixes=["["],
        skip_first_line=True,
        encoding_full_scan=settings.get_encoding_full_scan()
    )

    for row in edition_data:
        name = _parse_card_name_from_edition_row(row)
        if name:
            yield name

def get_edition_code(edition_name: str) -> str:
    """
    Retrieve the Forge edition code for an edition.

    The edition code uniquely identifies a Forge edition and is
    retrieved from the Forge edition-to-code map.

    Args:
        edition_name: The name of the edition to look up.

    Returns:
        The edition code associated with the edition.

    Raises:
        ValueError: If no edition code is defined for the specified
            edition.
    """
    code_map: DataMap = data_map_loader.get_forge_edition_to_code_map()
    edition_code: str | None = code_map.get(edition_name)

    if edition_code is not None:
        return edition_code
    
    raise ValueError(f"Edition code undefined for edition '{edition_name}'") 

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _parse_card_name_from_edition_row(row: str) -> str:
    """
    Parse a card name from a single row of a Forge edition file.

    Splits on the card delimiter and extracts the name starting from
    the expected token index. Returns an empty string if no name
    can be parsed, and logs a debug message in that case.

    Args:
        row: A single row string from the edition file.

    Returns:
        The parsed card name, or an empty string if parsing fails.
    """   
    line: str = row.split(forge_const.FORGE_EDITION_CARD_NAME_TERMINATOR, 1)[0]
    card_name: str = " ".join(line.split()[forge_const.FORGE_EDITION_CARD_NAME_FIELD:])
    
    if not card_name:
        logger.debug("Could not parse card name from row: %s", line)

    return card_name 