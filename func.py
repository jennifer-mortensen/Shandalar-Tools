import const
import csv
import chardet
import sys

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
    try:
        edition_data = get_csv_column(get_edition_file_path(edition_name), 0, ',', 0, '[cards]')
    except FileNotFoundError:
        return False, None
    for r in edition_data:
        cards.append(edition_data_row_to_card(r))
    return True, cards

# Returns the file path of an edition from a string.
def get_edition_file_path(edition_name):
    return const.data_path_editions + "/" + edition_name + ".txt"

# Returns the list of editions from the config file.
def get_editions_list():
    editions = get_csv_column(const.file_config, 0)
    return editions

# Returns the list of cards supported in Shandalar.
def get_shandalar_cards():
    return get_csv_column(const.file_shandalar_csv, const.shandalar_card_name_column)

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def get_unsupported_cards(cards):
    print('Checking incompatible cards...')
    unsupported_cards = []
    shandalar_cards = sanitize_array(get_shandalar_cards())
    
    for c in cards:
        if sanitize_name(c) not in shandalar_cards:
            unsupported_cards.append(c)
    print('Found ' + str(len(unsupported_cards)) + ' incompatible cards.')
    return unsupported_cards

# Add all cards from the given editions to the cards array.            
def populate_cards(cards, editions):
    editions_loaded = set()

    print('Compiling source card list...')
    for e in editions:
        print('Loading ' + e + '...')
        if sanitize_name(e) in editions_loaded:
            print('Duplicate detected. Skipping ' + e + '.')
        else:    
            success, edition_cards = get_edition_cards(e)
            if not success:
                print('Could not load file at ' + get_edition_file_path(e) + '.')
                print('Terminating application.')
                sys.exit(1)
            else:
                cards = list(set(cards + edition_cards))
                editions_loaded.add(sanitize_name(e))        
    return cards

# Returns a sanitized array. Removes leading/trailing spaces from all card names and converts them to lowercase.
def sanitize_array(cards):
    cards_sanitized = []
    for c in cards:
        cards_sanitized.append(sanitize_name(c))
    return cards_sanitized

# Returns a sanitized name string. Removes leading/trailing spaces and converts to lowercase.
def sanitize_name(name):
    return name.strip().lower()