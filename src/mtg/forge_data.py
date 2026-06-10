"""
Forge edition data access and parsing utilities.

Provides helpers for loading Forge edition files, extracting card
names, and retrieving edition metadata such as Scryfall set codes.
Used to build card pools and format data from Forge edition sources.
"""
from collections.abc import Iterable
from common import common_const, common_utils, file_utils, path_utils, runtime
from mtg import forge_const
from pathlib import Path
import json, logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_forge_card_name_lookup() -> dict[str, set[str]]:
    """
    Build a Forge card name lookup grouped by edition.

    Scans every Forge edition file and builds an in-memory lookup
    mapping edition names to the set of card names defined in that
    edition.

    Editions that contain no card definitions are skipped and logged as
    warnings.

    Returns:
        A mapping of Forge edition names to the set of card names
        contained in each edition.
    """    
    logger.info("Loading Forge card pool...")
    
    card_pool: dict[str, set[str]] = {}

    for file in common_const.FORGE_EDITIONS_DIR.glob(f"*{common_const.FILE_TYPE_FORGE_EDITION}"):
        edition_name: str = file.stem
        edition_cards: set[str] = set(get_edition_card_names(edition_name))
        if edition_cards:
            logger.debug("Loaded %d cards for edition '%s'", len(edition_cards), edition_name)
            card_pool[edition_name] = common_utils.sanitize_set(edition_cards)
        else:
            logger.warning("No cards found for edition '%s'.", edition_name)

    return card_pool  

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

def card_exists(edition_name: str, card_name: str, forge_card_name_lookup: dict[str, set[str]]) -> bool:
    """
    Determine whether a card exists in a Forge edition.

    Checks whether the provided card name exists in the specified Forge
    edition using a prebuilt card name lookup.

    Args:
        edition_name: The Forge edition to search.
        card_name: The card name to look up.
        forge_card_name_lookup: Mapping of Forge edition names to the set
            of card names contained in each edition.

    Returns:
        True if the card exists in the specified edition; otherwise False.

    Raises:
        KeyError: If the edition is not present in the lookup.
    """    
    # NOTE:
    # Deliberately uses direct indexing. A KeyError indicates a broken
    # invariant: every referenced edition must exist in the lookup.
    return common_utils.sanitize_string(card_name) in forge_card_name_lookup[edition_name]

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

def edition_codes_are_canonical(scryfall_code: str, forge_edition_code: str) -> bool:
    """
    Determine whether a Forge edition code is the canonical owner of a
    Scryfall code.

    A Forge edition is considered canonical when its Forge edition code
    matches its explicit Scryfall code.

    Args:
        scryfall_code: The Scryfall code associated with an edition.
        forge_edition_code: The Forge edition code associated with an
            edition.

    Returns:
        True if the Forge edition code is the canonical owner of the
        Scryfall code; otherwise False.
    """    
    return scryfall_code == forge_edition_code

def edition_is_canonical(edition_name: str) -> bool:
    """
    Determine whether an edition is the canonical owner of its Scryfall code.

    An edition is considered canonical when its explicit Scryfall code
    matches its Forge edition code. Editions without an explicit Scryfall
    code are not considered canonical.

    Args:
        edition_name: The Forge edition to evaluate.

    Returns:
        True if the edition is the canonical owner of its Scryfall code;
        otherwise False.
    """    
    scryfall_code: str | None = get_scryfall_code(edition_name=edition_name, allow_fallback=False)

    if scryfall_code is None:
        return False
    
    forge_edition_code: str = get_forge_edition_code(edition_name)

    return edition_codes_are_canonical(scryfall_code=scryfall_code, forge_edition_code=forge_edition_code)

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

def get_scryfall_code(edition_name: str, allow_fallback: bool = True) -> str | None:
    """
    Read the Scryfall code from a Forge edition file.

    Reads the edition's explicit Scryfall code when present. If no
    Scryfall code is defined and fallback is enabled, returns the
    edition's Forge code instead.

    Args:
        edition_name: The name of the edition to look up.
        allow_fallback: Whether to fall back to the Forge edition code
            when no explicit Scryfall code is defined.

    Returns:
        The explicit Scryfall code associated with the edition, the
        Forge edition code if fallback is enabled, or None if no
        Scryfall code is defined and fallback is disabled.

    Raises:
        ValueError: If fallback is enabled and neither a Scryfall code
            nor a Forge edition code is defined.
    """
    encoding_scan_mode: bool = runtime.get_encoding_scan_mode()
    file_path: Path = path_utils.build_edition_file_path(edition_name)

    scryfall_code: str | None = file_utils.read_text_field(
        file_path=file_path,
        field_prefix=forge_const.SCRYFALL_CODE_PREFIX,
        encoding_full_scan=encoding_scan_mode)

    if scryfall_code is not None or not allow_fallback:
        return scryfall_code
    
    try:
        forge_edition_code: str = get_forge_edition_code(edition_name)
        logger.warning(
            "Scryfall code undefined for edition '%s'. Using fallback from Forge edition code: '%s%s'.",
            edition_name,
            forge_const.FORGE_EDITION_CODE_PREFIX,
            forge_edition_code
        )
        return forge_edition_code        
    except ValueError as e:
        raise ValueError(f"Unable to resolve code for edition '{edition_name}'. Scryfall code and Forge edition code were both undefined.") from e

def get_forge_edition_code(edition_name: str) -> str:
    """
    Read the Forge edition code from a Forge edition file.

    The Forge edition code is defined by the edition's standard Code field
    and may be used as a fallback identifier when no explicit Scryfall code 
    is available.

    Args:
        edition_name: The name of the edition to look up.

    Returns:
        The Forge edition code associated with the edition.

    Raises:
        ValueError: If no Forge edition code is defined for the edition.
    """    
    encoding_scan_mode: bool = runtime.get_encoding_scan_mode()
    file_path: Path = path_utils.build_edition_file_path(edition_name)

    forge_edition_code: str | None = file_utils.read_text_field(
        file_path=file_path,
        field_prefix=forge_const.FORGE_EDITION_CODE_PREFIX,
        encoding_full_scan=encoding_scan_mode)

    if forge_edition_code is not None:
        return forge_edition_code
    
    raise ValueError(f"Forge edition code undefined for edition '{edition_name}'") 

def load_forge_edition_card_names(edition_name: str) -> set[str]:
    file_path: Path = path_utils.build_edition_file_path(edition_name)

def read_forge_scryfall_map() -> dict[str, str]:
    """
    Read the Forge Scryfall map.

    Loads the Forge Scryfall map from disk and returns the edition code
    mapping contained within the data file.

    Returns:
        Mapping of edition codes to Forge edition names.
    """
    logger.info("Loading Forge Scryfall map...")
    with path_utils.build_forge_scryfall_map_path().open("r", encoding="utf-8") as file:
        return json.load(file)[common_const.DATA_MAP_EDITION_CODE_FIELD]

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

    Returns:
        The parsed card name, or an empty string if parsing fails.
    """   
    line: str = row.split(forge_const.FORGE_EDITION_CARD_DELIMITER, 1)[0]
    card_name: str = " ".join(line.split()[forge_const.EDITIONS_CARD_NAME_STARTING_COLUMN:])
    
    if not card_name:
        logger.debug("Could not parse card name from row: %s", line)

    return card_name 