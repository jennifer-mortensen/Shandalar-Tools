"""
Forge edition data access and parsing utilities.

Provides helpers for loading Forge edition files, extracting card
names, and retrieving edition metadata such as Scryfall set codes.
Used to build card pools and format data from Forge edition sources.
"""
from collections.abc import Iterable
from common import common_utils, file_utils, path_utils, runtime
from mtg import forge_const
from pathlib import Path
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

    for e in edition_names:
        sanitized_edition_name: str = common_utils.sanitize_string(e)
        if sanitized_edition_name in editions_loaded:
            logger.warning("Duplicate edition '%s' detected; skipping.", e)
            continue

        logger.debug("Loading edition '%s'...", e)

        cards.update(get_edition_card_names(e))
        editions_loaded.add(sanitized_edition_name)

    return cards

def collect_scryfall_codes(edition_names: list[str]) -> set[str]:
    """
    Collect Scryfall edition codes for a list of edition names.

    Args:
        edition_names: Names of the editions to collect codes for.

    Returns:
        A set containing the Scryfall codes for the supplied editions.
    """   
    logger.info("Generating Scryfall edition codes...")
    
    scryfall_codes: set[str] = set()

    for e in edition_names:
        logger.debug("Collecting scryfall code for '%s'...", e)
        code = get_scryfall_code(e)
        scryfall_codes.add(code)

    return scryfall_codes

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
    file_path: Path = path_utils.build_edition_file_path(edition_name)

    edition_data = file_utils.read_text_section(
        file_path=file_path, 
        start_prefix=forge_const.FORGE_EDITION_CARDS_HEADER,
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

    Returns:
        The Scryfall code defined for the edition.

    Raises:
        ValueError: If no Scryfall code is defined for the edition.
    """ 
    file_path: Path = path_utils.build_edition_file_path(edition_name)

    try:
        line = next(file_utils.read_text_section(
            file_path=file_path,
            start_prefix=forge_const.SCRYFALL_CODE_PREFIX,
            encoding_full_scan=runtime.get_encoding_scan_mode()
        ))
    except StopIteration:
        raise ValueError(f"Edition {edition_name} has no Scryfall code defined.")

    return line[len(forge_const.SCRYFALL_CODE_PREFIX):]

def _parse_card_name_from_edition_row(row: str) -> str:
    """
    Parse a card name from a single row of a Forge edition file.

    Splits on the card delimiter and extracts the name starting from
    the expected column index. Returns an empty string if no name
    can be parsed, and logs a debug message in that case.

    Args:
        row: A single row string from the edition file.

    Returns:
        The parsed card name, or an empty string if parsing fails.
    """   
    line: str = row.split(forge_const.FORGE_EDITION_CARD_DELIMITER, 1)[0]
    card_name: str = " ".join(line.split()[forge_const.EDITIONS_CARD_NAME_STARTING_COLUMN:])
    
    if not card_name:
        logger.debug("Could not parse card name from row: %s", line)

    return card_name 