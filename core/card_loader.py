from core import const
from pathlib import Path
import csv
import logging

logger = logging.getLogger(__name__)

# ==============================
# HIGH LEVEL LOADERS
# ==============================

# Returns the matching Scryfall Code for the given edition name.
def get_edition_code(edition_name: str) -> str:
    if not edition_name:
        raise ValueError("Edition name cannot be empty.")

    scryfall_field = read_text_section(get_edition_file_path(edition_name), start_prefix=const.SCRYFALL_CODE_PREFIX, max_lines=1, skip_header=False)
     
    if not scryfall_field: 
        raise ValueError(f"Edition {edition_name} has no Scryfall code defined.")        

    line = scryfall_field[0]

    if not line.lower().startswith(const.SCRYFALL_CODE_PREFIX.lower()):
        raise ValueError(f"Malformed Scryfall code for {edition_name} with line: {line}")            

    return line[len(const.SCRYFALL_CODE_PREFIX):]

# Returns a set of cards from the given edition.
def get_edition_cards(edition_name: str) -> set[str]:
    if not edition_name:
        raise ValueError("Edition name cannot be empty.") 
    
    edition_data = read_text_section(get_edition_file_path(edition_name), const.FORGE_CARDS_HEADER, ["["])

    if not edition_data:
        logger.warning("No cards found for edition '%s'.", edition_name)
        return set()
    
    return {_parse_card_name_from_edition_row(r) for r in edition_data}

# Returns the list of editions from a csv config file.
def get_edition_list(csv_filename: str | Path) -> list[str]:
    return read_csv_column(csv_filename, 0, skip_prefixes=[const.COMMENT_PREFIX])

# Returns the list of cards supported in Shandalar.
def get_shandalar_cards() -> set[str]:
    cards = read_csv_column(const.FILE_SHANDALAR_CSV, const.SHANDALAR_CARD_NAME_STARTING_COLUMN)
    return set(cards) if cards else set()

# Returns a list of user-banned cards.
def get_user_banned_cards(filename: str | Path) -> list[str]:
    return read_csv_column(filename, 0, skip_prefixes=[const.COMMENT_PREFIX])

# ==============================
# CSV / TEXT UTILITIES
# ==============================

# Extract a column from a CSV file with optional filtering.
# Supports skipping rows by prefix, starting at a given index or header,
# and ignores empty/commented lines.
def read_csv_column(
    filename: str | Path,
    column_number: int,
    csv_delimiter: str = const.DEFAULT_CSV_DELIMITER, 
    starting_index: int = 0,
    starting_header: str = "",
    skip_prefixes: list[str] | None = None,
) -> list[str]:
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

# Get the encoding type for the file.
def detect_file_encoding(filename: str | Path) -> str:
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

# Extract a section from a text file with optional filtering.
# Supports skipping rows by prefix, starting at a given header,
# returning a specific number of lines, and ignores empty/commented lines.
def read_text_section(
    filename: str | Path,
    start_prefix: str = None,
    end_prefixes: list[str] | None = None,
    skip_prefixes: list[str] | None = None,
    max_lines: int = None,
    skip_header: bool = True,
) -> list[str]:
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
    if not edition_name:
        raise ValueError(f"Edition name cannot be empty.")

    return const.EDITIONS_DIR / f"{edition_name}{const.EDITION_FILE_SUFFIX}"

# Returns a normalized filename, which includes the given extension (if not already present).
def normalize_filename(filename: str, extension: str) -> Path:
    path = Path(filename)
    return path if path.suffix else path.with_suffix(f".{extension}")

# Returns a sanitized name string. Removes leading/trailing spaces and converts to lowercase.
def sanitize_name(name: str) -> str:
    return name.strip().lower()

# Returns a sanitized set. Removes leading/trailing spaces from all card names and converts them to lowercase.
def sanitize_card_set(cards: set[str]) -> set[str]:
    return {sanitize_name(c) for c in cards}

# ==============================
# PRIVATE HELPERS
# ==============================

# Returns the card name embedded within a row of Forge edition data.
def _parse_card_name_from_edition_row(row: str) -> str:
    line = row.split(const.FORGE_EDITION_CARD_DELIMITER, 1)[0]
    return " ".join(line.split()[const.EDITIONS_CARD_NAME_STARTING_COLUMN:])