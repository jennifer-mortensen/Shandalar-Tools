import const
import csv
import chardet
import os

# Returns the card name embedded within a row of edition data.
#   row (array) = the row e.g. as loaded via csv reader.
def edition_data_row_to_card(row):
    return " ".join(row.split(" ")[const.editions_card_name_starting_column:]).split(" @")[0]

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

    with open(file_name, newline = "", encoding = get_csv_encoding(file_name)) as csvfile:
        reader = csv.reader(csvfile, delimiter = csv_delimiter)
        for i, row in enumerate(reader):
            if(read_data == True):
                if(row == []):
                    # Stop reading once we find no further data.
                    break    
                return_val.append(row[column_number])
            elif(row != [] and (starting_header == "" or row[0] == starting_header) and i >= starting_index):
                read_data = True

    return return_val

# Get the encoding type for the file.
def get_csv_encoding(file_name):
    with open(file_name, "rb") as file:
        return chardet.detect(file.read())["encoding"]

# Returns a set of cards from the given edition.
def get_edition_cards(edition_name):
    try:
        edition_data = get_csv_column(get_edition_file_path(edition_name), 0, ',', 0, "[cards]")
    except FileNotFoundError:
        return None
    
    return {edition_data_row_to_card(r) for r in edition_data}

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