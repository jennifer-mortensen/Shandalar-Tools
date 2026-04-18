"""
CLI entry point for the Shandalar → MTG: Forge compatibility tool.

Orchestrates the full workflow:
- Parses command-line arguments
- Loads edition and card data
- Identifies unsupported cards
- Incorporates user-defined bans
- Generates and writes Forge-compatible output

Also configures logging for both user-facing CLI output and detailed file logs.
"""
from core import card_loader, card_processor, const
from pathlib import Path # Used for typing.
import argparse
import logging
import sys

logger = logging.getLogger(__name__)

# ==============================
# MAIN ENTRY POINT
# ==============================

def main() -> None:
    """
    Execute the CLI workflow for generating an MTG: Forge format file.

    This function parses command-line arguments, loads and processes
    card data, generates the Forge format, and writes the output file.
    """    
    configure_logging()
    
    try:
        cli_args = parse_cli_args()
        
        # Load data
        edition_list = load_edition_list(cli_args.editions)
        card_pool = build_card_pool(edition_list)

        # Build banned card pool            
        unsupported_cards = find_unsupported_cards(card_pool)
        user_banned_cards = load_user_banned_cards(cli_args.user_banned)               

        # Format and write
        logger.info("Formatting output for MTG: Forge...")
        forge_output = card_processor.build_forge_format(unsupported_cards, user_banned_cards, card_processor.collect_edition_codes(edition_list))        
        write_forge_output(forge_output, cli_args.output)

        logger.info("Compilation completed successfully!")
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception:
        logger.exception("Unexpected error")
        # Separate CLI-level output. Full exception is logged externally just above.
        print(
            f"ERROR: An unexpected error occurred. "
            f"See the log file (default: {card_loader.normalize_filename(const.FILE_NAME_LOG, const.FILE_TYPE_LOG)}) for details."
        )
        sys.exit(1)

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================

def configure_logging() -> None:
    """
    Configure logging for both CLI and file output.

    CLI logging displays human-readable messages, while file logging
    includes debug information and full exception tracebacks.
    """    
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
        mode=const.LOGGER_FILE_MODE,
        encoding=const.DEFAULT_ENCODING
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [console, file_handler]

def parse_cli_args() -> argparse.Namespace:
    """
    Parse and return command-line arguments.

    Returns:
        An argparse.Namespace containing normalized file paths for
        input and output files.
    """    
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

def load_edition_list(editions_filename: str | Path) -> list[str]:
    """
    Load the list of editions from a configuration file.

    Args:
        editions_filename: Path to the editions CSV file.

    Returns:
        A list of edition names.

    Raises:
        ValueError: If the file is missing or empty.
    """    
    logger.info("Loading edition list...")

    try:
        editions = card_loader.get_edition_list(editions_filename)
    except FileNotFoundError:
        raise ValueError(f"Could not find editions file: {editions_filename}")
    if not editions:
        raise ValueError(f"Editions file is empty: {editions_filename}")

    return editions

def build_card_pool(editions: list[str]) -> set[str]:
    """
    Build the card pool from the specified editions.

    Args:
        editions: A list of edition names.

    Returns:
        A set of unique card names.
    """    
    logger.info("Building card pool from editions...")
    card_pool = card_processor.build_card_pool(editions)

    if not card_pool:
        logger.warning("No cards were loaded from the specified editions. Edition files may be empty, missing, or invalid.")

    return card_pool

def find_unsupported_cards(card_pool: set[str]) -> list[str]:
    """
    Identify cards that are unsupported by Shandalar.

    Args:
        card_pool: A set of card names.

    Returns:
        A list of unsupported card names.
    """    
    logger.info("Identifying unsupported cards...")
    shandalar_lookup = card_processor.build_shandalar_card_lookup()        
    
    unsupported_cards = card_processor.find_unsupported_cards(card_pool, shandalar_lookup)        
    if not unsupported_cards:
        logger.warning("No unsupported cards found among %d cards. This is unexpected and may indicate an issue with the input data or configuration.", len(card_pool))

    return unsupported_cards

def load_user_banned_cards(user_banned_filename: str | Path) -> list[str]:
    """
    Load user-defined banned cards from a file.

    Args:
        user_banned_filename: Path to the CSV file.

    Returns:
        A list of user-banned card names. Returns an empty list if the
        file does not exist.
    """    
    logger.info("Loading user-banned card list...")

    try:
        user_banned_cards = card_loader.get_user_banned_cards(user_banned_filename)
    except FileNotFoundError:
        logger.warning("Could not find user-banned file: %s", user_banned_filename)
        return []

    if not user_banned_cards:
        logger.info("User-banned file is empty.")

    return user_banned_cards

def write_forge_output(forge_format: str, output_filename: str | Path) -> None:
    """
    Write the Forge format string to an output file.

    Args:
        forge_format: The generated Forge format string.
        output_filename: Path to the output file.

    Raises:
        OSError: If the file cannot be written.
    """    
    logger.info("Writing Forge output to %s...", output_filename)
    try:
        with open(output_filename, "w", encoding=const.DEFAULT_ENCODING) as file:
            file.write(forge_format)
    except OSError as e:
        raise OSError(f"Could not write to output file '{output_filename}': {e}") from e

if __name__ == "__main__":
    main()