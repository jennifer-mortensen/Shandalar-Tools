import const
import csv
import chardet

# Returns the card name embedded within a row of edition data.
#   row (array) = the row e.g. as loaded via csv reader.
def edition_data_row_to_card(row):
    columns = row.split(' ')
    row_right = ' '.join(columns[const.editions_card_name_starting_column:])
    card = row_right.split(' @')[0]
    return card

# Returns the column of a csv file as an array.
#   file_name (string) = the name (and path) of the file
#   column_number (int) = the index of the column to read
#   csv_delimiter (string) = the delimiter used to separate columns
#   starting_index (int) = the starting row number      
#   starting_header (string) = the header from which to start reading data; the header itself will be ignored
def get_csv_column(file_name, column_number, csv_delimiter = ',', starting_index = 0, starting_header = ''):
    return_val = []
    read_data = True

    if(starting_header != '' or starting_index > 0):
        read_data = False

    with open(file_name, newline = '', encoding = get_csv_encoding(file_name)) as csvfile:
        reader = csv.reader(csvfile, delimiter = csv_delimiter)
        for i, row in enumerate(reader):
            if(read_data == True):
                if(row == []):
                    # Stop reading once we find no further data.
                    break    
                return_val.append(row[column_number])
            elif(row != [] and (starting_header == '' or row[0] == starting_header) and i >= starting_index):
                read_data = True

    return return_val

# Get the encoding type for the file.
def get_csv_encoding(file_name):
    with open(file_name, 'rb') as file:
        return chardet.detect(file.read())['encoding']

# Returns a list of cards from the given edition.
def get_edition_cards(edition_name):
    cards = []
    edition_data = get_csv_column(const.data_path_editions + "/" + edition_name + ".txt", 0, ',', 0, '[cards]')
    for r in edition_data:
        cards.append(edition_data_row_to_card(r))
    return cards

# Returns the list of editions from the config file.
def get_editions_list():
    editions = get_csv_column(const.file_config, 0)
    return editions

# Returns the list of cards supported in Shandalar.
def get_shandalar_cards():
    return get_csv_column(const.file_shandalar_csv, const.shandalar_card_name_column)

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def get_unsupported_cards(cards):
    unsupported_cards = []
    shandalar_cards = sanitize_card_list(get_shandalar_cards())
    
    for c in cards:
        if sanitize_card_name(c) not in shandalar_cards:
            unsupported_cards.append(c)
    return unsupported_cards

# Add all cards from the given editions to the cards array.            
def populate_cards(cards, editions):
    for e in editions:
        cards = list(set(cards + get_edition_cards(e)))
    return cards

# Returns a sanitized card list. Removes leading/trailing spaces from all card names and converts them to lowercase.
def sanitize_card_list(cards):
    cards_sanitized = []
    for c in cards:
        cards_sanitized.append(sanitize_card_name(c))
    return cards_sanitized

# Returns a sanitized card name string. Removes leading/trailing spaces and converts to lowercase.
def sanitize_card_name(name):
    return name.strip().lower()