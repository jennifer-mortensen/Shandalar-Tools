import const
import csv
import chardet
import os

# Returns the card name embedded within a row of edition data.
#   row (string) = a Forge card line from the edition File
def edition_data_row_to_card(row):
    line = row.split(" @", 1)[0]
    return " ".join(line.split()[const.editions_card_name_starting_column:])

# Returns the column of a csv file as an array.
#   file_name (string) = the name (and path) of the file
#   column_number (int) = the index of the column to read
#   csv_delimiter (string) = the delimiter used to separate columns
#   starting_index (int) = the starting row number      
#   starting_header (string) = the header from which to start reading data; the header itself will be ignored
def get_csv_column(file_name, column_number, csv_delimiter = ",", starting_index = 0, starting_header = ""):
    return_val = []
    read_data = True

    if(starting_header != "" or starting_index > 0):
        read_data = False

    with open(file_name, newline = "", encoding = get_file_encoding(file_name)) as csvfile:
        reader = csv.reader(csvfile, delimiter = csv_delimiter)
        for i, row in enumerate(reader):      
            if(read_data == True):
                if(row == []):
                    # Ignore empty lines.
                    continue    
                return_val.append(row[column_number])
            elif(row != [] and (starting_header == "" or row[0] == starting_header) and i >= starting_index):
                read_data = True

    return return_val

# Returns a text section from a text file.
#   file_name (string) = the name (and path) of the file
#   start_prefix (string) = the prefix where we should begin reading text (e.g. [cards])
#   end_prefixes (list) = list of prefixes to stop reading at
#   skip_prefixes (list) = list of prefixes for lines from where data should not be read (default: "['#']")
#   max_line (int) = maximum number of lines to read
#   skip_header (boolean) = if true and a start_prefix is set, do not read the first line
def get_text_file_section(file_name, start_prefix = None, end_prefixes = None, skip_prefixes = None, max_lines = None, skip_header = True):
    section_lines = []
    read_data = False

    # Normalize prefixes
    if start_prefix is not None:
        start_prefix = start_prefix.lower()
    end_prefixes = [p.lower() for p in (end_prefixes or [])]
    skip_prefixes = [p.lower() for p in (skip_prefixes or ['#'])]

    with open(file_name, encoding = get_file_encoding(file_name)) as text_file:
        for line in text_file:
            line = line.strip()
            line_lower = line.lower()
            
            if not read_data:
                # If we aren't reading data yet, check if we should begin doing so now.                
                if start_prefix is None or line_lower.startswith(start_prefix):
                    read_data = True
                    # Skip the first line if we were waiting for a prefix. This avoids including
                    # section headers.
                    if start_prefix is not None and skip_header:
                        continue
                # We're still not reading data, so continue to the next line.
                else:
                    continue

            # If we have been reading data, check if we should stop doing so now.
            elif end_prefixes and any(line_lower.startswith(prefix) for prefix in end_prefixes):
                break            

            # Skip blank lines and compare to our list of prefixes to see if we should ignore this line.
            if line == "" or any(line_lower.startswith(prefix) for prefix in skip_prefixes):
                continue

            section_lines.append(line)
            if max_lines is not None and len(section_lines) >= max_lines:
                break

    return section_lines

# Get the encoding type for the file.
def get_file_encoding(file_name):
    with open(file_name, "rb") as file:
        return chardet.detect(file.read())["encoding"]

# Returns a set of cards from the given edition.
def get_edition_cards(edition_name):
    try:
        edition_data = get_text_file_section(get_edition_file_path(edition_name), "[cards]", ["["])
    except FileNotFoundError:
        return None
    
    return {edition_data_row_to_card(r) for r in edition_data}

# Returns the scryfall code for an edition.
def get_edition_code(edition_name):
    start_prefix = "ScryfallCode="
    max_lines = 1
    skip_header = False

    try:
        scryfall_field = get_text_file_section(get_edition_file_path(edition_name), start_prefix, None, None, max_lines, skip_header)
    except FileNotFoundError:
        print("File not found error")
        return None
    
    try:
        print("ScryfallField = " + str(scryfall_field))
        return scryfall_field[0].split("=", 1)[1]
    except IndexError:
        print("Index error")
        return None

# Returns the file path of an edition from a string.
def get_edition_file_path(edition_name):
    return os.path.join(const.data_path_editions + "/" + edition_name + ".txt")

# Returns the list of editions from a csv config file.
def get_editions_list(csv_filename):
    return get_csv_column(csv_filename, 0)

# Returns the list of cards supported in Shandalar.
def get_shandalar_cards():
    return set(get_csv_column(const.file_shandalar_csv, const.shandalar_card_name_column))

# Returns a sanitized set. Removes leading/trailing spaces from all card names and converts them to lowercase.
def sanitize_set(cards):
    return {sanitize_name(c) for c in cards}

# Returns a sanitized name string. Removes leading/trailing spaces and converts to lowercase.
def sanitize_name(name):
    return name.strip().lower()