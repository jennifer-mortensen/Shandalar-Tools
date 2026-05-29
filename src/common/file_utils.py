"""
File reading and encoding utilities for Shandalar Tools.

Provides helpers for detecting file encoding, reading CSV columns,
reading sections of text files, and safely opening files with
automatic encoding detection.
"""
from collections.abc import Iterator
from common import common_const, common_utils
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, TextIO
import csv
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def detect_file_encoding(file_path: Path, full_scan: bool = False) -> str:
    """
    Detect the encoding of a file by attempting to decode its contents.

    Tries each encoding defined in common_const.FILE_ENCODINGS in order,
    returning the first one that succeeds. Falls back to FALLBACK_ENCODING
    if none match.

    Args:
        file_path: Path to the file to inspect.
        full_scan: If True, reads the entire file. If False, reads only
            the first 10 KB.
    """    
    read_size: int = -1 if full_scan else common_const.FILE_ENCODING_READ_SIZE_DEFAULT

    with file_path.open("rb") as file:
        raw_data = file.read(read_size)

    for enc in common_const.FILE_ENCODINGS:
        try:
            raw_data.decode(encoding=enc)
            return enc
        except UnicodeDecodeError:
            continue

    # Safe fallback if no encoding detected
    logger.warning("Failed to detect file encoding for %s. Using %s fallback.", file_path, common_const.FALLBACK_ENCODING)
    return common_const.FALLBACK_ENCODING

def ensure_extension(file_path: Path, extension: str) -> Path:
    """
    Append an extension to a file path if one is not already present.

    Args:
        file_path: The path to check.
        extension: The extension to append, without a leading dot.
    """    
    return file_path if file_path.suffix else file_path.with_suffix(f".{extension}")

def load_raw_file(path: Path, encoding_full_scan: bool = False) -> str:
    """
    Read and return the full contents of a text file.

    Opens the file using automatic encoding detection and returns the
    entire file contents as a single string.

    Args:
        path: Path to the file to read.
        encoding_full_scan: If True, scans the entire file when detecting
            encoding. If False, scans only a partial portion of the file.

    Returns:
        The full contents of the file as a string.

    Raises:
        OSError: If the file cannot be opened or read.
    """    
    with open_file(path, encoding_full_scan=encoding_full_scan) as file:
        return file.read()

@contextmanager
def open_file(file_path: Path, encoding_full_scan: bool = False, newline: str | None = None) -> Iterator[TextIO]:
    """
    Context manager for opening a file with automatic encoding detection.

    Detects the file encoding before opening, either from a partial or full
    read depending on encoding_full_scan.

    Args:
        file_path: Path to the file to open.
        encoding_full_scan: If True, reads the entire file to detect encoding.
            If False, reads only the first 10,240 bytes.
        newline: Newline handling mode passed to the file open call.

    Raises:
        OSError: If the file cannot be opened.
    """    
    encoding: str = detect_file_encoding(file_path=file_path, full_scan=encoding_full_scan)
    try:
        with file_path.open(mode="r", encoding=encoding, newline=newline) as file:
            yield file
    except OSError as e:
        raise OSError(f"Could not open '{file_path}': {e}") from e

def read_csv_column(
    file_path: Path,
    column_number: int,
    csv_delimiter: str = common_const.DEFAULT_CSV_DELIMITER, 
    skip_prefixes: str | list[str] | None = None,
    encoding_full_scan: bool = False
) -> Iterator[str]:
    """
    Read a single column from a CSV file, yielding one value per row.

    Skips blank lines and any rows whose first cell starts with a
    specified prefix. Logs a warning for rows that do not contain
    the requested column.

    Args:
        file_path: Path to the CSV file.
        column_number: Zero-based index of the column to read.
        csv_delimiter: Delimiter character used in the CSV file.
        skip_prefixes: One or more prefixes that indicate rows to skip.
            Comparison is case-insensitive.
        encoding_full_scan: If True, reads the entire file to detect encoding.
            If False, reads only the first 10,240 bytes.
    """    
    skip_prefixes = [p.lower() for p in common_utils.to_list(skip_prefixes)]

    with open_file(file_path=file_path, encoding_full_scan=encoding_full_scan, newline="") as file:
        reader = csv.reader(file, delimiter=csv_delimiter)

        for i, row in enumerate(reader):
            # Check blank lines
            if not row:
                continue
            
            # Check skip prefixes
            cell_lower: str = row[0].strip().lower()
            if skip_prefixes and common_utils.has_any_prefix(line=cell_lower, prefixes=skip_prefixes):
                continue

            if column_number < len(row):
                yield row[column_number]
            else:
                logger.warning("Row %d has no column %d in %s. Row may be malformed.", i, column_number, file_path)

def read_csv_rows(
    file_path: Path,
    csv_delimiter: str = common_const.DEFAULT_CSV_DELIMITER,
    encoding_full_scan: bool = False
) -> Iterator[list[str]]:
    """
    Read a CSV file and yield rows as lists of fields.

    Opens the CSV file using automatic encoding detection and yields each
    parsed row as a list of string fields.

    Args:
        file_path: Path to the CSV file.
        csv_delimiter: Delimiter character used in the CSV file.
        encoding_full_scan: If True, reads the entire file to detect
            encoding. If False, reads only the first 10,240 bytes.

    Yields:
        Parsed CSV rows as lists of string fields.
    """    
    with open_file(file_path=file_path, encoding_full_scan=encoding_full_scan, newline="") as file:
        reader = csv.reader(file, delimiter=csv_delimiter)

        for row in reader:
            yield row  
            
def read_text_section(
    file_path: Path,
    start_prefix: str | None = None,
    end_prefixes: str | list[str] | None = None,
    skip_prefixes: str | list[str] | None = "#",
    skip_first_line: bool = False,
    encoding_full_scan: bool = False
) -> Iterable[str]:
    """
    Read a section of a text file, yielding one line at a time.

    Optionally begins reading at a line matching start_prefix, stops
    at a line matching any end_prefix, and skips lines matching any
    skip_prefix. Blank lines are always skipped.

    Args:
        file_path: Path to the text file.
        start_prefix: If provided, reading begins at the first line that
            starts with this prefix. If None, reading begins at the start
            of the file.
        end_prefixes: One or more prefixes that indicate the end of the
            section. Reading stops when a matching line is encountered.
        skip_prefixes: One or more prefixes that indicate lines to skip.
            Defaults to "#" to skip comment lines.
        skip_first_line: If True, skips the line that matches start_prefix
            before yielding. Useful when the header line itself is not needed.
        encoding_full_scan: If True, reads the entire file to detect encoding.
            If False, reads only the first 10,240 bytes.
    """    
    is_reading: bool = start_prefix is None
    start_prefix = start_prefix.lower() if start_prefix else None
    end_prefixes = [p.lower() for p in common_utils.to_list(end_prefixes)]
    skip_prefixes = [p.lower() for p in common_utils.to_list(skip_prefixes)]

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
            elif end_prefixes and common_utils.has_any_prefix(line=line_lower, prefixes=end_prefixes):
                break

            # Check skip prefixes
            if common_utils.has_any_prefix(line=line_lower, prefixes=skip_prefixes):
                continue
            
            yield clean_line

# ==============================
# PRIVATE FUNCTIONS
# ==============================
