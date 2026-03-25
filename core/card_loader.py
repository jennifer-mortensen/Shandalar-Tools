from core import const
import csv
import logging
import os

logger = logging.getLogger(__name__)

# ==============================
# HIGH LEVEL LOADERS
# ==============================

# Returns the matching Scryfall Code for the given edition name.
def get_edition_code(edition_name):
    if not edition_name:
        raise ValueError("edition_name returned empty.")

    scryfall_field = get_text_file_section(get_edition_file_path(edition_name), start_prefix=const.SCRYFALL_CODE_PREFIX, max_lines=1, skip_header=False)

    if scryfall_field is None:
        raise FileNotFoundError(f"Could not find edition code for {edition_name}.")             
    if len(scryfall_field) == 0: # explicitly checking empty vs missing
        raise ValueError(f"Could not find edition code for {edition_name}.")        

    line = scryfall_field[0]

    if not line.lower().startswith(const.SCRYFALL_CODE_PREFIX.lower()):
        raise ValueError(f"Malformed Scryfall code for {edition_name} with line: {line}")            

    return line[len(const.SCRYFALL_CODE_PREFIX):]

# Returns a set of cards from the given edition.
def get_edition_cards(edition_name):
    if not edition_name:
        raise ValueError(f"Edition name was invalid: {edition_name}") 
    
    edition_data = get_text_file_section(get_edition_file_path(edition_name), const.FORGE_CARDS_HEADER, ["["])

    if not edition_data:
        logger.warning(f"Card list for edition {edition_name} returned empty.")
        return set()
    
    return {_edition_data_row_to_card(r) for r in edition_data}

# Returns the list of editions from a csv config file.
def get_editions_list(csv_filename):
    return get_csv_column(csv_filename, 0, skip_prefixes=[const.COMMENT_PREFIX])

# Returns the list of cards supported in Shandalar.
def get_shandalar_cards():
    cards = get_csv_column(const.FILE_SHANDALAR_CSV, const.SHANDALAR_CARD_NAME_STARTING_COLUMN)
    return set(cards) if cards else set()

# Returns a list of user-banned cards.
def get_user_banned_cards(filename):
    # Optional file: None means file not found
    return get_csv_column(filename, 0, skip_prefixes=[const.COMMENT_PREFIX])

# ==============================
# CSV / TEXT UTILITIES
# ==============================

# NOTE:
# This function returns None if the file cannot be found.
# Callers are responsible for determining whether a missing file is an error
# or an acceptable condition (e.g., optional inputs).
#
# Returns the column of a csv file as an array.
#   filename (string) = the name (and path) of the file
#   column_number (int) = the index of the column to read
#   csv_delimiter (string) = the delimiter used to separate columns
#   starting_index (int) = the starting row number      
#   starting_header (string) = the header from which to start reading data; the header itself will be ignored
#   skip_prefixes (list) = list of prefixes used to designate that a row should not be read
def get_csv_column(filename, column_number, csv_delimiter=const.DEFAULT_CSV_DELIMITER, starting_index=0, starting_header="", skip_prefixes=None):
    csv_column = []
    read_data = not (starting_header or starting_index > 0)

    try:
        with open(filename, newline = "", encoding = get_file_encoding(filename)) as csvfile:
            reader = csv.reader(csvfile, delimiter = csv_delimiter)
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
    except FileNotFoundError:
        return None

    return csv_column

# Get the encoding type for the file.
def get_file_encoding(filename):
    for enc in const.FILE_ENCODINGS:
        try:
            with open(filename, encoding=enc) as f:
                f.read()
            return enc
        except UnicodeDecodeError:
            continue

    # Safe fallback if no encoding detected
    return const.FALLBACK_ENCODING

# NOTE:
# This function returns None if the file cannot be found.
# Callers are responsible for determining whether a missing file is an error
# or an acceptable condition (e.g., optional inputs).
#
# Returns a text section from a text file.
#   filename (string) = the name (and path) of the file
#   start_prefix (string) = the prefix where we should begin reading text (e.g. [cards])
#   end_prefixes (list) = list of prefixes to stop reading at
#   skip_prefixes (list) = list of prefixes for lines from where data should not be read (default: "['#']")
#   max_lines (int) = maximum number of lines to read
#   skip_header (boolean) = if true and a start_prefix is set, do not read the first line
def get_text_file_section(filename, start_prefix=None, end_prefixes=None, skip_prefixes=None, max_lines=None, skip_header=True):
    section_lines = []
    read_data = start_prefix is None

    # Normalize prefixes
    if start_prefix is not None:
        start_prefix = start_prefix.lower()
    end_prefixes = [p.lower() for p in (end_prefixes or [])]
    skip_prefixes = [p.lower() for p in (skip_prefixes or ['#'])]

    try:
        with open(filename, encoding = get_file_encoding(filename)) as text_file:
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
    except FileNotFoundError:
        return None

    return section_lines

# ==============================
# PUBLIC HELPERS
# ==============================

# Returns the file path of an edition from a string.
def get_edition_file_path(edition_name):
    if not edition_name:
        return None    
    return os.path.join(const.DATA_PATH_EDITIONS, edition_name + const.EDITION_FILE_SUFFIX)

# Returns a normalized filename, which includes the given extension (if not already present).
def normalize_filename(filename, extension):
    return filename if os.path.splitext(filename)[1] else f"{filename}.{extension}"

# Returns a sanitized name string. Removes leading/trailing spaces and converts to lowercase.
def sanitize_name(name):
    return name.strip().lower()

# Returns a sanitized set. Removes leading/trailing spaces from all card names and converts them to lowercase.
def sanitize_set(cards):
    return {sanitize_name(c) for c in cards}

# ==============================
# PRIVATE HELPERS
# ==============================

# Returns the card name embedded within a row of edition data.
#   row (string) = a Forge card line from the edition File
def _edition_data_row_to_card(row):
    line = row.split(const.FORGE_EDITION_CARD_DELIMITER, 1)[0]
    return " ".join(line.split()[const.EDITIONS_CARD_NAME_STARTING_COLUMN:])