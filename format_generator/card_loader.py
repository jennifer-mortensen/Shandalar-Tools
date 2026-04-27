"""
Data loading and file parsing utilities.

Responsible for:
- Reading edition data and extracting card names and metadata
- Loading CSV-based configuration (editions, banned cards, Shandalar data)
- Handling text section extraction from Forge files
- Detecting file encodings and normalizing filenames
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

def get_edition_list(csv_filename: str | Path) -> list[str]:
    """
    Load a list of edition names from a CSV configuration file.

    Args:
        csv_filename: Path to the CSV file.

    Returns:
        A list of edition names.
    """    
    return read_csv_column(csv_filename, 0, skip_prefixes=[const.COMMENT_PREFIX])

def get_shandalar_cards() -> set[str]:
    """
    Load the set of cards supported by Shandalar.

    Returns:
        A set of supported card names.
    """    
    cards = read_csv_column(filename=const.FILE_SHANDALAR_CSV, column_number=const.SHANDALAR_CARD_NAME_STARTING_COLUMN, encoding_full_scan=True)
    return set(cards) if cards else set()

def get_user_banned_cards(filename: str | Path) -> list[str]:
    """
    Load user-defined banned cards from a CSV file.

    Args:
        filename: Path to the user-banned cards file.

    Returns:
        A list of banned card names.
    """    
    return read_csv_column(filename, 0, skip_prefixes=[const.COMMENT_PREFIX])

# ==============================
# CSV / TEXT UTILITIES
# ==============================

def read_csv_column(
    filename: str | Path,
    column_number: int,
    csv_delimiter: str = const.DEFAULT_CSV_DELIMITER, 
    starting_index: int = 0,
    starting_header: str = "",
    skip_prefixes: list[str] | None = None,
    encoding_full_scan: bool = False
) -> list[str]:
    """
    Extract a column of data from a CSV file with optional filtering.

    Args:
        filename: Path to the CSV file.
        column_number: The index of the column to extract.
        csv_delimiter: The delimiter used in the CSV file.
        starting_index: The row index at which to begin reading.
        starting_header: A header value that marks the start of data.
        skip_prefixes: Line prefixes that should be ignored.
        ending_full_scan: If true, reads the whole file for encoding. If false, sniffs the first 10KB.

    Returns:
        A list of extracted values.

    Raises:
        ValueError: If the specified column does not exist.
    """    
    csv_column = []
    read_data = not (starting_header or starting_index > 0)

    encoding = detect_file_encoding(filename, encoding_full_scan)
    with open(filename, newline="", encoding=encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=csv_delimiter)
        for i, row in enumerate(reader):      
            header_condition_met = not starting_header or (row and row[0] == starting_header)
            if read_data:
                if not row or (skip_prefixes and any(row[0].startswith(p) for p in skip_prefixes)):
                    # Ignore empty lines or those that start with a given prefix to be skipped.
                    continue    
                if column_number < len(row):
                    csv_column.append(row[column_number])
                else:
                    raise ValueError(f"Could not find csv data at row {i}, column {column_number} in {filename}: {row}")
            elif row and header_condition_met and i >= starting_index:
                read_data = True

    return csv_column

def detect_file_encoding(file_path: Path, full_scan: bool = False) -> str:
    """
    Detects the encoding of a file.
    
    Args:
        file_path: Path to the file.
        full_scan: If True, reads the whole file. If False, sniffs the first 10KB.
    """
    read_size = -1 if full_scan else const.FILE_ENCODING_READ_SIZE_DEFAULT

    with file_path.open('rb') as f:
        raw_data = f.read(read_size)

    for enc in const.FILE_ENCODINGS:
        try:
            raw_data.decode(enc)
            return enc
        except (UnicodeDecodeError):
            continue

    # Safe fallback if no encoding detected
    return const.FALLBACK_ENCODING

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

    Yields:
        str: Each non-empty, stripped line found between the prefixes.
    """
    is_reading = start_prefix is None
    start_prefix = start_prefix.lower() if start_prefix else None
    end_prefixes = [p.lower() for p in to_list(end_prefixes)]
    skip_prefixes = [p.lower() for p in to_list(skip_prefixes)]

    with file_path.open('r', encoding=encoding) as f:
        for line in f:
            if not (clean_line := line.strip()):
                continue

            line_lower = clean_line.lower()

            if not is_reading:
                if start_prefix and line_lower.startswith(start_prefix):
                    is_reading = True
                    if skip_header:
                        continue
                else:
                    continue

            elif end_prefixes and any(line_lower.startswith(p) for p in end_prefixes):
                break

            if any(line_lower.startswith(p) for p in skip_prefixes):
                continue

            yield clean_line

# ==============================
# PUBLIC HELPERS
# ==============================

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

def normalize_filename(filename: str, extension: str) -> Path:
    """
    Ensure a filename includes the specified extension.

    Args:
        filename: The filename to normalize.
        extension: The required file extension.

    Returns:
        A Path object with the correct extension.
    """    
    path = Path(filename)
    return path if path.suffix else path.with_suffix(f".{extension}")

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