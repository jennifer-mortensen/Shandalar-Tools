from core import card_loader, card_processor, const
from pathlib import Path # used for typing
import argparse
import logging
import sys

logger = logging.getLogger(__name__)

# ==============================
# MAIN ENTRY POINT
# ==============================

def main() -> None:
    initiate_logging()
    
    try:
        args = parse_args()
        
        # Load data
        editions = load_editions(args.editions)
        source_cards = build_source_cards(editions)

        # Build banned card pool            
        unsupported_cards = compute_unsupported_cards(source_cards)
        user_banned_cards = load_user_banned_cards(args.user_banned)               

        # Format and write
        forge_format = format_cards(unsupported_cards, user_banned_cards, editions)
        write_forge_format(forge_format, args.output)

        logger.info("Compilation complete!")
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception:
        logger.exception("Unexpected error")
        # Separate CLI-level output. Full exception is logged externally just above.
        print(
            f"ERROR: Unexpected error occurred. "
            f"See log file (default: {card_loader.normalize_filename(const.FILE_NAME_LOG, const.FILE_TYPE_LOG)}) for details."
        )
        sys.exit(1)

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================

# Initializes logging:
# - CLI: INFO, WARNING, ERROR (human-readable)
# - File: CLI output + DEBUG and full exception tracebacks (diagnostic detail)
def initiate_logging() -> None:
    formatter = logging.Formatter(const.LOGGER_FORMAT_FILE)

    # CLI-level logging. Prioritize readability.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(const.LOGGER_FORMAT_CLI))

    # Filter out exception tracebacks from CLI
    class NoExceptionTracebackFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.exc_info is None

    console.addFilter(NoExceptionTracebackFilter())

    # File-level logging. Full fidelity.
    file_handler = logging.FileHandler(
        card_loader.normalize_filename(const.FILE_NAME_LOG, const.FILE_TYPE_LOG),
        mode=const.LOGGER_WRITE_BEHAVIOR,
        encoding=const.DEFAULT_ENCODING
    )
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
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-o", "--output",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_OUTPUT),
        default=card_loader.normalize_filename(const.FILE_NAME_OUTPUT, const.FILE_TYPE_OUTPUT),
        help="File to write unsupported cards to.",
    )
    parser.add_argument(
        "-e", "--editions",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_CONFIG),
        default=card_loader.normalize_filename(const.FILE_NAME_CONFIG, const.FILE_TYPE_CONFIG),
        help="CSV file listing editions to load.",
    )
    parser.add_argument(
        "-b", "--user-banned",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_USER_BANNED),
        default=card_loader.normalize_filename(const.FILE_NAME_USER_BANNED, const.FILE_TYPE_USER_BANNED),
        help="CSV file listing user-designated cards to ban.",
    )

    return parser.parse_args()  

# Loads and returns user-defined editions file as a list.
def load_editions(editions_filename: str | Path) -> list[str]:
    logger.info("Checking editions to load...")

    try:
        editions = card_loader.get_editions_list(editions_filename)
    except FileNotFoundError:
        raise ValueError(f"Could not find editions file: {editions_filename}")
    if not editions:
        raise ValueError(f"Editions file is empty: {editions_filename}")

    return editions

# Returns all existing cards from the given editions as a set.
def build_source_cards(editions: list[str]) -> set[str]:
    logger.info("Compiling source card list...")
    source_cards = card_processor.get_card_pool(editions)

    if not source_cards:
        logger.warning("No cards were loaded from the provided editions. All edition files may be empty or invalid.")

    return source_cards

# Compares the given cards to Shandalar's data and returns unsupported cards as a list.
def compute_unsupported_cards(source_cards: set[str]) -> list[str]:
    logger.info("Checking unsupported cards...")
    shandalar_lookup = card_processor.build_shandalar_lookup()        
    
    unsupported_cards = card_processor.get_unsupported_cards(source_cards, shandalar_lookup)        
    if not unsupported_cards:
        logger.warning("No unsupported cards found among %d cards. This is highly unusual and may indicate an issue with the input data or configuration.", len(source_cards))

    return unsupported_cards

# Loads all cards from the user_banned file.
def load_user_banned_cards(user_banned_filename: str | Path) -> list[str]:
    logger.info("Loading user-banned cards...")

    try:
        user_banned_cards = card_loader.get_user_banned_cards(user_banned_filename)
    except FileNotFoundError:
        logger.warning("Could not find user-banned file: %s", user_banned_filename)
        return []

    if not user_banned_cards:
        logger.info("User-banned file is empty.")

    return user_banned_cards

# Using the given pool of unsupported cards (i.e. not included in Shandalar), user-defined bans, and editions, generate a valid Forge format and return as a string.
def format_cards(unsupported_cards: list[str], user_banned_cards: list[str], editions: list[str]) -> str:
    logger.info("Formatting cards to MTG: Forge format...")
    forge_format = card_processor.generate_forge_format(unsupported_cards, user_banned_cards, card_processor.generate_edition_codes(editions))

    return forge_format    

# Writes the Forget format string to the given output file.
def write_forge_format(forge_format: str, output_filename: str | Path) -> None:
    logger.info("Writing unsupported cards to %s...", output_filename)
    try:
        with open(output_filename, "w", encoding=const.DEFAULT_ENCODING) as file:
            file.write(forge_format)
    except OSError as e:
        raise OSError(f"Could not write to output file '{output_filename}': {e}") from e

if __name__ == "__main__":
    main()