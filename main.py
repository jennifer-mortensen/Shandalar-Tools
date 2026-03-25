from core import card_loader, card_processor, const
import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ==============================
# MAIN ENTRY POINT
# ==============================

def main():
    args = parse_args()
    editions = load_editions(args.editions)
    source_cards = compile_source_cards(editions)
    unsupported_cards = compute_unsupported_cards(source_cards)
    user_banned_cards = load_user_banned_cards(args.user_banned)
    forge_format = format_cards(unsupported_cards, user_banned_cards, editions)
    write_forge_format(forge_format, args.output)

    print("Compilation complete!")

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================

# Prepares args.
# output = file to output format to (i.e. the generated Forge format)
# editions = the file containing a list of editions to be loaded
# user_banned = the file containing optional additional cards to be added to the banned list
def parse_args():
    parser = argparse.ArgumentParser(
        prog="shandalar-tools", 
        description="Check card compatibility between Shandalar and MTG: Forge.",
        epilog="Examples:\n  %(prog)s\n  %(prog)s -e custom_sets.csv\n  %(prog)s -o unsupported.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument(
        "-o", "--output",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_OUTPUT),
        default=const.FILE_NAME_OUTPUT,
        help="File to write unsupported cards to."
    )
    parser.add_argument(
        "-e", "--editions",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_CONFIG),
        default=const.FILE_NAME_CONFIG,
        help="CSV file listing editions to load."                  
    )
    parser.add_argument(
        "-b", "--user-banned",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_USER_BANNED),
        default=const.FILE_NAME_USER_BANNED,
        help="CSV file listing user-designated cards to ban."                  
    )    
    return parser.parse_args()         

# Loads and returns user-defined editions file as a list.
def load_editions(editions_filename):
    print("Checking editions to load...")
    try:
        editions = card_loader.get_editions_list(editions_filename)
    except ValueError as e:
        fail(e)

    require_non_empty(editions, "editions file", editions_filename)    

    return editions

# Returns all existing cards from the given editions as a set.
def compile_source_cards(editions):
    print("Compiling source card list...")
    try:
        source_cards = card_processor.get_card_pool(editions)
    except ValueError as e:
        fail(e)
    
    if not source_cards:
        fail("No cards were loaded from the provided editions. All edition files may be empty or invalid.")

    return source_cards

# Compares the given cards to Shandalar's data and returns unsupported cards as a list.
def compute_unsupported_cards(source_cards):
    print("Checking unsupported cards...")
    try:
        shandalar_lookup = card_processor.build_shandalar_lookup()        
    except ValueError as e:
        fail(e)        
    
    unsupported_cards = card_processor.get_unsupported_cards(source_cards, shandalar_lookup)        
    if not unsupported_cards:
        print(f"WARNING: No unsupported cards found among {len(source_cards)} cards. This is highly unusual and may indicate an issue with the input data or configuration.")

    return unsupported_cards

# Loads and returns user-defined bans as a list.    
def load_user_banned_cards(user_banned_file_name):
    print("Loading user-banned cards...")
    try:
        user_banned_cards = card_loader.get_user_banned_cards(user_banned_file_name)
    except ValueError as e:
        fail(e)

    handle_optional(user_banned_cards, "user-banned cards")    

    return user_banned_cards 

# Using the given pool of unsupported cards (i.e. not included in Shandalar), user-defined bans, and editions, generate a valid Forge format and return as a string.
def format_cards(unsupported_cards, user_banned_cards, editions):
    print("Formatting cards to MTG: Forge format...")
    try:
        forge_format = card_processor.generate_forge_format(unsupported_cards, user_banned_cards, card_processor.generate_edition_codes(editions))
    except ValueError as e:
        fail(e)

    return forge_format    

# Writes the forget format string to the given output file.
def write_forge_format(forge_format, output_filename):
    print(f"Writing unsupported cards to {output_filename}...")
    try:
        with open(output_filename, "w", encoding=const.DEFAULT_ENCODING) as file:
            file.write(forge_format)
    except OSError as e:
        fail(f"Could not write to output file: {e}")

# ==============================
# HELPERS
# ==============================

# Exits the program with the given error.
def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)

# Verifies that the file contains useful data.
# Specify whether the file did not exist or if it was empty on failure.
# Terminates the application.
def require_non_empty(data, name, filename):
    if data is None:
        fail(f"Could not find {name}: {filename}")
    if len(data) == 0:
        fail(f"{name.capitalize()} is empty: {filename}")
    return data

# Verifies that the file contains useful data.
# Specify whether the file did not exist or if it was empty on failure.
# Warns the user.
def handle_optional(data, name):
    if data is None:
        print(f"WARNING: Could not find {name}.")
        return None
    if len(data) == 0:
        print(f"WARNING: {name.capitalize()} was found, but list was empty.")
    return data    

# ==============================

if __name__ == "__main__":
    main()