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

    scryfall_field = read_text_section(get_edition_file_path(edition_name), start_prefix=const.SCRYFALL_CODE_PREFIX, max_lines=1, skip_header=False)
     
    if not scryfall_field: 
        raise ValueError(f"Edition {edition_name} has no Scryfall code defined.")        

    line = scryfall_field[0]

    if not line.lower().startswith(const.SCRYFALL_CODE_PREFIX.lower()):
        raise ValueError(f"Malformed Scryfall code for {edition_name} with line: {line}")            

    return line[len(const.SCRYFALL_CODE_PREFIX):]

def get_edition_cards(edition_name: str) -> set[str]:
    """
    Load all card names from a Forge edition file.

    Args:
        edition_name: The name of the edition.

    Returns:
        A set of card names contained in the edition.
    """    
    if not edition_name:
        raise ValueError("Edition name cannot be empty.") 
    
    edition_data = read_text_section(get_edition_file_path(edition_name), const.FORGE_CARDS_HEADER, ["["])

    if not edition_data:
        logger.warning("No cards found for edition '%s'.", edition_name)
        return set()
    
    return {_parse_card_name_from_edition_row(r) for r in edition_data}

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
    cards = read_csv_column(const.FILE_SHANDALAR_CSV, const.SHANDALAR_CARD_NAME_STARTING_COLUMN)
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

    Returns:
        A list of extracted values.

    Raises:
        ValueError: If the specified column does not exist.
    """    
    csv_column = []
    read_data = not (starting_header or starting_index > 0)

    encoding = detect_file_encoding(filename)
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

def detect_file_encoding(filename: str | Path) -> str:
    """
    Detect the encoding of a file.

    Args:
        filename: Path to the file.

    Returns:
        The detected encoding, or a fallback encoding if detection fails.
    """    
    for enc in const.FILE_ENCODINGS:
        try:
            with open(filename, encoding=enc) as f:
                # Full read required. Partial reads may miss encoding issues in Shandalar data.
                f.read()
            return enc
        except UnicodeDecodeError:
            continue

    # Safe fallback if no encoding detected
    return const.FALLBACK_ENCODING

def read_text_section(
    filename: str | Path,
    start_prefix: str = None,
    end_prefixes: list[str] | None = None,
    skip_prefixes: list[str] | None = None,
    max_lines: int = None,
    skip_header: bool = True,
) -> list[str]:
    """
    Extract a section of text from a file with optional filtering.

    Args:
        filename: Path to the text file.
        start_prefix: Prefix indicating where to begin reading.
        end_prefixes: Prefixes indicating where to stop reading.
        skip_prefixes: Prefixes for lines to ignore.
        max_lines: Maximum number of lines to read.
        skip_header: Whether to skip the starting line.

    Returns:
        A list of extracted lines.
    """    
    section_lines = []
    read_data = start_prefix is None

    # Normalize prefixes
    if start_prefix is not None:
        start_prefix = start_prefix.lower()
    end_prefixes = [p.lower() for p in (end_prefixes or [])]
    skip_prefixes = [p.lower() for p in (skip_prefixes or ['#'])]

    encoding = detect_file_encoding(filename)
    with open(filename, encoding=encoding) as text_file:
        for line in text_file:
            line = line.strip()
            line_lower = line.lower()
               
            if not read_data:
                # If we're still not reading data, then abort this loop if the start condition isn't met.            
                if not line_lower.startswith(start_prefix):
                    continue

                read_data = True
                # Skip the first line if told to do so.
                if skip_header:
                    continue
 
            # If we have been reading data, check if we should stop doing so now.
            elif end_prefixes and any(line_lower.startswith(prefix) for prefix in end_prefixes):
                break            

            # Skip blank lines and compare to our list of prefixes to see if we should ignore this line.
            if not line or any(line_lower.startswith(prefix) for prefix in skip_prefixes):
                continue

            section_lines.append(line)
            if max_lines is not None and len(section_lines) >= max_lines:
                break

    return section_lines

# ==============================
# PUBLIC HELPERS
# ==============================

# Returns the file path of an edition from a string.
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