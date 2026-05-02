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

import sys
from pathlib import Path
print(Path(__file__).parent.parent / "src")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import common_const
from config.format_generator_config import FormatGeneratorConfig
from config.common_config import CommonConfig
import argparse
import logging
from format_generator import card_loader, card_processor

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
        common = CommonConfig(io_encoding_scan=common_const.EncodingScanMode(cli_args.encoding_scan))
        config = FormatGeneratorConfig(common=common)
        
        # Load data
        edition_list = load_edition_list(editions_file_path=cli_args.editions, config=config)
        card_pool = build_card_pool(editions=edition_list, config=config)

        # Build banned card pool            
        unsupported_cards = resolve_unsupported_cards(card_pool=card_pool, config=config)
        user_banned_cards = load_user_banned_cards(user_banned_file_path=cli_args.user_banned, config=config)             

        # Format and write
        logger.info("Formatting output for MTG: Forge...")
        forge_output = card_processor.build_forge_format(
            unsupported_cards=unsupported_cards,
            user_banned_cards=user_banned_cards,
            edition_codes=card_processor.collect_edition_codes(edition_list, config=config)
        )        
        write_forge_output(forge_format=forge_output, output_file_path=cli_args.output)

        logger.info("Compilation completed successfully!")
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception:
        logger.exception("Unexpected error")
        # Separate CLI-level output. Full exception is logged externally just above.
        log_path = common_const.LOG_DIR / f"{common_const.FILE_NAME_LOG}.{common_const.FILE_TYPE_LOG}"        
        print(f"ERROR: An unexpected error occurred. See the log file (default: {log_path}) for details.")
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
    formatter = logging.Formatter(common_const.LOGGER_FORMAT_FILE)

    # CLI-level logging. Prioritize readability.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(common_const.LOGGER_FORMAT_CLI))

    # Filter out exception tracebacks from CLI
    class NoExceptionTracebackFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.exc_info is None

    console.addFilter(NoExceptionTracebackFilter())

    # File-level logging. Full fidelity.
    file_handler = logging.FileHandler(
        common_const.LOG_DIR / f"{common_const.FILE_NAME_LOG}.{common_const.FILE_TYPE_LOG}",
        mode=common_const.LOGGER_FILE_MODE,
        encoding=common_const.DEFAULT_ENCODING
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [console, file_handler]

def parse_cli_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the CLI.

    Returns:
        An argparse.Namespace containing normalized input and output paths
        and configuration options.
    """    
    parser = argparse.ArgumentParser(
        prog="shandalar-tools",
        description="Check card compatibility between Shandalar and MTG: Forge.",
        epilog="Examples:\n  %(prog)s\n  %(prog)s -e custom_sets.csv\n  %(prog)s -o unsupported.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-o", "--output",
        type=lambda file_name: card_loader.ensure_extension(
            file_path=Path(file_name),
            extension=common_const.FILE_TYPE_OUTPUT
        ),
        default=card_loader.ensure_extension(
            file_path=common_const.USER_OUTPUT_DIR / common_const.FILE_NAME_OUTPUT,
            extension=common_const.FILE_TYPE_OUTPUT
        ),
        help="File to write unsupported cards to.",
    )
    parser.add_argument(
        "-e", "--editions",
        type=lambda file_name: card_loader.ensure_extension(
            file_path=Path(file_name),
            extension=common_const.FILE_TYPE_CONFIG
        ),
        default=card_loader.ensure_extension(
            file_path=common_const.USER_CONFIG_DIR / common_const.FILE_NAME_CONFIG,
            extension=common_const.FILE_TYPE_CONFIG
        ),
        help="CSV file listing editions to load.",
    )
    parser.add_argument(
        "-b", "--user-banned",
        type=lambda file_name: card_loader.ensure_extension(
            file_path=Path(file_name),
            extension=common_const.FILE_TYPE_USER_BANNED
        ),
        default=card_loader.ensure_extension(
            file_path=common_const.USER_CONFIG_DIR / common_const.FILE_NAME_USER_BANNED,
            extension=common_const.FILE_TYPE_USER_BANNED
        ),
        help="CSV file listing user-designated cards to ban.",
    )
    parser.add_argument(
        "-s", "--encoding-scan",
        default="auto",
        choices=["auto", "fast", "full"],
        help=(
            "Encoding detection mode: "
            "auto (use built-in defaults), "
            "fast (partial read, faster but may miss issues), "
            "full (scan entire file, slower but reliable)."
        )
    )

    return parser.parse_args()  

def load_edition_list(editions_file_path: Path, config: format_generator_config.FormatGeneratorConfig) -> list[str]:
    """
    Load edition names from a configuration file.

    Args:
        editions_file_path: Path to the editions CSV file.
        config: FormatGeneratorConfig controlling encoding behavior.

    Returns:
        A list of edition names.

    Raises:
        ValueError: If the file is missing or empty.
    """  
    logger.info("Loading edition list...")

    try:
        editions = card_loader.get_edition_list(csv_file_path=editions_file_path, config=config)
    except FileNotFoundError:
        raise ValueError(f"Could not find editions file: {editions_file_path}")
    if not editions:
        raise ValueError(f"Editions file is empty: {editions_file_path}")

    return editions

def build_card_pool(editions: list[str], config: format_generator_config.FormatGeneratorConfig) -> set[str]:
    """
    Build the card pool from the specified editions.

    Args:
        editions: A list of edition names.
        config: FormatGeneratorConfig controlling encoding behavior.

    Returns:
        A set of unique card names.
    """
    logger.info("Building card pool from editions...")
    card_pool = card_processor.build_card_pool(editions=editions, config=config)

    if not card_pool:
        logger.warning("No cards were loaded from the specified editions. Edition files may be empty, missing, or invalid.")

    return card_pool

def resolve_unsupported_cards(card_pool: set[str], config: format_generator_config.FormatGeneratorConfig) -> list[str]:
    """
    Resolve cards that are unsupported by Shandalar.

    Builds the Shandalar lookup and delegates comparison to the processor.

    Args:
        card_pool: A set of card names.
        config: FormatGeneratorConfig controlling encoding behavior.

    Returns:
        A list of unsupported card names.
    """
    logger.info("Identifying unsupported cards...")
    shandalar_lookup = card_processor.build_shandalar_card_lookup(config=config)        
    
    unsupported_cards = card_processor.find_unsupported_cards(cards=card_pool, shandalar_lookup=shandalar_lookup)        
    if not unsupported_cards:
        logger.warning(
            "No unsupported cards found among %d cards. This is unexpected and may indicate an issue with the "
             "input data or configuration.", len(card_pool)
        )

    return unsupported_cards

def load_user_banned_cards(user_banned_file_path: Path, config: format_generator_config.FormatGeneratorConfig) -> list[str]:
    """
    Load user-defined banned cards from a file.

    Args:
        user_banned_file_path: Path to the CSV file.
        config: FormatGeneratorConfig controlling encoding behavior.

    Returns:
        A list of user-banned card names, or an empty list if the file is missing.
    """   
    logger.info("Loading user-banned card list...")

    try:
        user_banned_cards = card_loader.get_user_banned_cards(file_path=user_banned_file_path, config=config)
    except FileNotFoundError:
        logger.warning("Could not find user-banned file: %s", user_banned_file_path)
        return []

    if not user_banned_cards:
        logger.info("User-banned file is empty.")

    return user_banned_cards

def write_forge_output(forge_format: str, output_file_path: Path) -> None:
    """
    Write the Forge format string to an output file.

    Args:
        forge_format: The generated Forge format string.
        output_file_path: Path to the output file.

    Raises:
        OSError: If the file cannot be written.
    """    
    logger.info("Writing Forge output to %s...", output_file_path)
    try:
        with output_file_path.open("w", encoding=common_const.DEFAULT_ENCODING) as file:
            file.write(forge_format)
    except OSError as e:
        raise OSError(f"Could not write to output file '{output_file_path}': {e}") from e

if __name__ == "__main__":
    main()