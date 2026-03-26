from core import card_loader, card_processor, const
import argparse
import logging
import sys
from typing import NoReturn

logger = logging.getLogger(__name__)

# ==============================
# MAIN ENTRY POINT
# ==============================

def main() -> None:
    initiate_logging()
    args = parse_args()
    editions = load_editions(args.editions)
    source_cards = build_source_cards(editions)
    unsupported_cards = compute_unsupported_cards(source_cards)
    user_banned_cards = load_user_banned_cards(args.user_banned)
    forge_format = format_cards(unsupported_cards, user_banned_cards, editions)
    write_forge_format(forge_format, args.output)

    logger.info("Compilation complete!")

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================

# Prepares and initiates the formatter.
# Separates high-level CLI log from DEBUG, which is added to a log file (default: app.log)
def initiate_logging() -> None:
    formatter = logging.Formatter(const.LOGGER_FORMAT_FILE)

    # CLI-level logging. Prioritize readability.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(const.LOGGER_FORMAT_CLI))

    # File-level logging. Full fidelity.
    file_handler = logging.FileHandler(
        card_loader.normalize_filename(const.FILE_NAME_LOG, const.FILE_TYPE_LOG),
        mode=const.LOGGER_WRITE_BEHAVIOR, encoding=const.DEFAULT_ENCODING)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [console, file_handler]

# Prepares args.
# output = file to output format to (i.e. the generated Forge format)
# editions = the file containing a list of editions to be loaded
# user_banned = the file containing optional additional cards to be added to the banned list
def parse_args() -> argparse.Namespace:
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
def load_editions(editions_filename) -> list[str]:
    logger.info("Checking editions to load...")
    try:
        editions = card_loader.get_editions_list(editions_filename)
    except ValueError as e:
        fail(e)

    require_non_empty(editions, "editions file", editions_filename)
    assert editions is not None # narrow type for type checker after validation

    return editions

# Returns all existing cards from the given editions as a set.
def build_source_cards(editions) -> set[str]:
    logger.info("Compiling source card list...")
    try:
        source_cards = card_processor.get_card_pool(editions)
    except ValueError as e:
        fail(e)
    
    if not source_cards:
        fail("No cards were loaded from the provided editions. All edition files may be empty or invalid.")

    return source_cards

# Compares the given cards to Shandalar's data and returns unsupported cards as a list.
def compute_unsupported_cards(source_cards) -> list[str]:
    logger.info("Checking unsupported cards...")
    try:
        shandalar_lookup = card_processor.build_shandalar_lookup()        
    except ValueError as e:
        fail(e)        
    
    unsupported_cards = card_processor.get_unsupported_cards(source_cards, shandalar_lookup)        
    if not unsupported_cards:
        logger.warning("No unsupported cards found among %d cards. This is highly unusual and may indicate an issue with the input data or configuration.", len(source_cards))

    return unsupported_cards

# Loads and returns user-defined bans as a list.    
def load_user_banned_cards(user_banned_file_name) -> list[str] | None:
    logger.info("Loading user-banned cards...")
    try:
        user_banned_cards = card_loader.get_user_banned_cards(user_banned_file_name)
    except ValueError as e:
        fail(e)

    handle_optional(user_banned_cards, "user-banned cards")    

    return user_banned_cards 

# Using the given pool of unsupported cards (i.e. not included in Shandalar), user-defined bans, and editions, generate a valid Forge format and return as a string.
def format_cards(unsupported_cards, user_banned_cards, editions) -> str:
    logger.info("Formatting cards to MTG: Forge format...")
    try:
        forge_format = card_processor.generate_forge_format(unsupported_cards, user_banned_cards, card_processor.generate_edition_codes(editions))
    except ValueError as e:
        fail(e)

    return forge_format    

# Writes the Forget format string to the given output file.
def write_forge_format(forge_format, output_filename) -> None:
    logger.info("Writing unsupported cards to %s...", output_filename)
    try:
        with open(output_filename, "w", encoding=const.DEFAULT_ENCODING) as file:
            file.write(forge_format)
    except OSError as e:
        fail(f"Could not write to output file: {e}")

# ==============================
# HELPERS
# ==============================

# Exits the program with the given error.
def fail(message) -> NoReturn:
    logger.error(message)
    sys.exit(1)

# Verifies that the file contains useful data.
# Specify whether the file did not exist or if it was empty on failure.
# Terminates the application.
def require_non_empty(data, name, filename) -> None:
    if data is None:
        fail(f"Could not find {name}: {filename}")
    elif len(data) == 0:
        fail(f"{name.capitalize()} is empty: {filename}")

# Verifies that the file contains useful data.
# Specify whether the file did not exist or if it was empty on failure.
# Warns the user.
def handle_optional(data, name) -> None:
    if data is None:
        logger.warning("Could not find %s.", name)
    elif len(data) == 0:
        logger.warning("%s was found, but list was empty.", name.capitalize())  

# ==============================

if __name__ == "__main__":
    main()