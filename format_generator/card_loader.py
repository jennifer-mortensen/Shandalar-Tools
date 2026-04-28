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
from format_generator import const
from pathlib import Path
from typing import Iterable
import csv
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
    encoding = detect_file_encoding(file_path)

    try:
        line = next(read_text_section(file_path, encoding, start_prefix=const.SCRYFALL_CODE_PREFIX))
    except StopIteration:
        raise ValueError(f"Edition {edition_name} has no Scryfall code defined.")

    if not line.lower().startswith(const.SCRYFALL_CODE_PREFIX.lower()):
        raise ValueError(f"Malformed Scryfall code for {edition_name} with line: {line}")

    return line[len(const.SCRYFALL_CODE_PREFIX):] 

def get_edition_cards(edition_name: str) -> Iterable[str]:
    """
    Load all card names from a Forge edition file.

    Args:
        edition_name: The name of the edition.

    Yields:
        Card names from a Forge edition file.
    """    
    if not edition_name:
        raise ValueError("Edition name cannot be empty.") 
    
    file_path = get_edition_file_path(edition_name)
    encoding = detect_file_encoding(file_path)

    edition_data = read_text_section(file_path, encoding, const.FORGE_CARDS_HEADER, ["["])

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
    return read_csv_column(csv_file_path, 0, skip_prefixes=[const.COMMENT_PREFIX])

def get_shandalar_cards() -> set[str]:
    """
    Load the set of cards supported by Shandalar.

    Returns:
        A set of supported card names.
    """    
    cards = read_csv_column(file_path=const.FILE_SHANDALAR_CSV, column_number=const.SHANDALAR_CARD_NAME_STARTING_COLUMN, encoding_full_scan=True)
    return set(cards)

def get_user_banned_cards(file_path: Path) -> list[str]:
    """
    Load user-defined banned cards from a CSV file.

    Args:
        file_path: Path to the user-banned cards file.

    Returns:
        A list of banned card names.
    """    
    return list(read_csv_column(file_path=file_path, column_number=0, skip_prefixes=[const.COMMENT_PREFIX]))

# ==============================
# CSV / TEXT UTILITIES
# ==============================

def detect_file_encoding(file_path: Path, full_scan: bool = False) -> str:
    """
    Detects the encoding of a file.
    
    Args:
        file_path: Path to the file.
        full_scan: If True, reads the whole file. If False, sniffs the first 10KB.
    """
    read_size = -1 if full_scan else const.FILE_ENCODING_READ_SIZE_DEFAULT

    with file_path.open("rb") as file:
        raw_data = file.read(read_size)

    for enc in const.FILE_ENCODINGS:
        try:
            raw_data.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue

    # Safe fallback if no encoding detected
    return const.FALLBACK_ENCODING

def read_csv_column(
    file_path: Path,
    column_number: int,
    csv_delimiter: str = const.DEFAULT_CSV_DELIMITER, 
    skip_prefixes: str | list[str] | None = None,
    encoding_full_scan: bool = False
) -> Iterable[str]:
    """
    Extract a column of data from a CSV file with optional filtering.

    Args:
        file_path: Path to the CSV file.
        column_number: The index of the column to extract.
        csv_delimiter: The delimiter used in the CSV file.
        skip_prefixes: Line prefixes that should be ignored.
        encoding_full_scan: If true, reads the whole file for encoding. If false, sniffs the first 10KB.

    Returns:
        An iterable of extracted values.

    Raises:
        ValueError: If the specified column does not exist.
    """    
    skip_prefixes = [p.lower() for p in to_list(skip_prefixes)]

    encoding = detect_file_encoding(file_path, encoding_full_scan)
    with file_path.open("r", newline="", encoding=encoding) as file:
        reader = csv.reader(file, delimiter=csv_delimiter)

        for i, row in enumerate(reader):
            # Skip blank lines
            if not row:
                continue
            
            # Skip rows that are designed to be skipped
            cell_lower = row[0].strip().lower()
            if skip_prefixes and _has_any_prefix(cell_lower, skip_prefixes):
                continue

            if column_number < len(row):
                yield row[column_number]
            else:
                raise ValueError(f"Missing column {column_number} at row {i} in {file_path}: {row}")
            
def read_text_section(
    file_path: Path,
    encoding: str,
    start_prefix: str | None = None,
    end_prefixes: str | list[str] | None = None,
    skip_prefixes: str | list[str] | None = "#",
    skip_header: bool = True,
) -> Iterable[str]:
    """
    Yields lines from a file that fall between specific prefixes.

    Args:
        file_path: Path to the text file.
        start_prefix: Prefix indicating where to begin reading.
        end_prefixes: Prefixes indicating where to stop reading.
        skip_prefixes: Prefixes for lines to ignore.
        skip_header: Whether to skip the starting line.

    Returns:
        An iterable of each non-empty, stripped line found between the prefixes.
    """
    is_reading = start_prefix is None
    start_prefix = start_prefix.lower() if start_prefix else None
    end_prefixes = [p.lower() for p in to_list(end_prefixes)]
    skip_prefixes = [p.lower() for p in to_list(skip_prefixes)]

    with file_path.open("r", encoding=encoding) as file:
        for line in file:
            if not (clean_line := line.strip()):
                continue

            line_lower = clean_line.lower()

            # Check if reading should begin
            if not is_reading:
                if start_prefix and line_lower.startswith(start_prefix):
                    is_reading = True
                    if skip_header:
                        continue
                else:
                    continue

            # Check if reading should end
            elif end_prefixes and _has_any_prefix(line_lower, end_prefixes):
                break

            # Skip lines that are designated to be skipped
            if _has_any_prefix(line_lower, skip_prefixes):
                continue
            yield clean_line            

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

    return const.EDITIONS_DIR / f"{edition_name}{const.EDITION_FILE_SUFFIX}"

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

def to_list(value: str | Iterable[str]) -> list[str]:
    """
    Normalize input into a list.

    Behavior:
    - None → []
    - Iterable (excluding str/bytes) → list(value)
    - Single value (including str/bytes) → [value]

    This prevents strings/bytes from being split into elements while still
    allowing lists, tuples, sets, and other iterables to pass through.

    Args:
        value: A single item, an iterable of items, or None.

    Returns:
        A list containing the normalized values.
    """    
    if value is None:
        return []
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return list(value)
    return [value]

# ==============================
# PRIVATE HELPERS
# ==============================

def _has_any_prefix(line: str, prefixes: list[str]):
    """
    Return True if the given string starts with any of the provided prefixes.

    Comparison is case-sensitive. Callers are responsible for normalizing
    inputs (e.g., lowercasing) if case-insensitive behavior is desired.

    Args:
        line: The string to evaluate.
        prefixes: A list of prefixes to check against.

    Returns:
        True if the string starts with any prefix in the list, otherwise False.
    """
    return any(line.startswith(p) for p in prefixes)

def _parse_card_name_from_edition_row(row: str) -> str:
    """
    Extract a card name from a Forge edition data row.

    Args:
        row: A line from a Forge edition file.

    Returns:
        The parsed card name.
    """    
    line = row.split(const.FORGE_EDITION_CARD_DELIMITER, 1)[0]
    return " ".join(line.split()[const.EDITIONS_CARD_NAME_STARTING_COLUMN:])