from pathlib import Path
from typing import Iterable
from common import common_const
from contextlib import contextmanager
import csv
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC UTILITIES
# ==============================

def detect_file_encoding(file_path: Path, full_scan: bool = False) -> str:
    """
    Detects the encoding of a file.
    
    Args:
        file_path: Path to the file.
        full_scan: If True, reads the whole file. If False, sniffs the first 10KB.
    """
    read_size = -1 if full_scan else common_const.FILE_ENCODING_READ_SIZE_DEFAULT

    with file_path.open("rb") as file:
        raw_data = file.read(read_size)

    for enc in common_const.FILE_ENCODINGS:
        try:
            raw_data.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue

    # Safe fallback if no encoding detected
    logger.warning("Failed to detect file encoding for %s. Using %s fallback.", file_path, common_const.FALLBACK_ENCODING)
    return common_const.FALLBACK_ENCODING

@contextmanager
def open_file(file_path: Path, encoding_full_scan: bool = False, newline: str | None = None):
    """
    Open a text file with automatic encoding detection and error handling.

    Args:
        file_path: Path to the file to open.
        encoding_full_scan: If True, reads the whole file for encoding detection.
            If False, sniffs the first 10KB.
        newline: Newline handling mode. Pass an empty string for CSV files to
            preserve line endings for the csv module. Defaults to None.

    Yields:
        An open file object.

    Raises:
        OSError: If the file cannot be opened.
    """    
    encoding = detect_file_encoding(file_path=file_path, full_scan=encoding_full_scan)
    try:
        with file_path.open("r", encoding=encoding, newline=newline) as file:
            yield file
    except OSError as e:
        raise OSError(f"Could not open '{file_path}': {e}") from e

def read_csv_column(
    file_path: Path,
    column_number: int,
    csv_delimiter: str = common_const.DEFAULT_CSV_DELIMITER, 
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
        encoding_full_scan: If True, reads the whole file for encoding detection.
            If False, sniffs the first 10KB.

    Yields:
        Values from the specified column, one per row.

    Raises:
        OSError: If the file cannot be opened.
    """  
    skip_prefixes = [p.lower() for p in to_list(skip_prefixes)]

    with open_file(file_path=file_path, encoding_full_scan=encoding_full_scan, newline="") as file:
        reader = csv.reader(file, delimiter=csv_delimiter)

        for i, row in enumerate(reader):
            # Check blank lines
            if not row:
                continue
            
            # Check skip prefixes
            cell_lower = row[0].strip().lower()
            if skip_prefixes and _has_any_prefix(cell_lower, skip_prefixes):
                continue

            if column_number < len(row):
                yield row[column_number]
            else:
                logger.warning("Row %d has no column %d in %s. Row may be malformed.", i, column_number, file_path)
            
def read_text_section(
    file_path: Path,
    start_prefix: str | None = None,
    end_prefixes: str | list[str] | None = None,
    skip_prefixes: str | list[str] | None = "#",
    skip_first_line: bool = False,
    encoding_full_scan: bool = False
) -> Iterable[str]:
    """
    Yield lines from a file that fall between specific prefixes.

    Args:
        file_path: Path to the text file.
        start_prefix: Prefix indicating where to begin reading. If None,
            reading begins from the start of the file.
        end_prefixes: Prefixes indicating where to stop reading.
        skip_prefixes: Prefixes for lines to ignore. Defaults to "#".
        skip_first_line: If True, skips the line that matches start_prefix
            and begins yielding from the following line.
        encoding_full_scan: If True, reads the whole file for encoding detection.
            If False, sniffs the first 10KB.

    Yields:
        Non-empty, stripped lines found between the specified prefixes.

    Raises:
        OSError: If the file cannot be opened.
    """
    is_reading = start_prefix is None
    start_prefix = start_prefix.lower() if start_prefix else None
    end_prefixes = [p.lower() for p in to_list(end_prefixes)]
    skip_prefixes = [p.lower() for p in to_list(skip_prefixes)]

    with open_file(file_path=file_path, encoding_full_scan=encoding_full_scan) as file:
        for line in file:
            if not (clean_line := line.strip()):
                continue

            line_lower = clean_line.lower()

            # Check start prefix
            if not is_reading:
                if start_prefix and line_lower.startswith(start_prefix):
                    is_reading = True
                    if skip_first_line:
                        continue
                else:
                    continue

            # Check end prefixes
            elif end_prefixes and _has_any_prefix(line_lower, end_prefixes):
                break

            # Check skip prefixes
            if _has_any_prefix(line_lower, skip_prefixes):
                continue
            
            yield clean_line

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