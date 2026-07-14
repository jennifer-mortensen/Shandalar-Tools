"""
Generate the Forge edition to code map.

Scans Forge edition files and builds a mapping of edition codes to
Forge edition names. The generated map is used to resolve edition
identifiers across data sources and is written to the Forge data
directory as JSON.
"""
from common import args, file_utils, log_utils, paths, path_const, runtime, settings
from common.file_types import EncodingScanMode
from mtg import forge_const
from pathlib import Path
from resources import data_map_const
from resources.data_map import DataMap
import argparse, logging, sys

logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
TOOL_NAME: str = "forge_code_map_generator"
LOG_NAME: str = TOOL_NAME
CLI_PROG: str = TOOL_NAME
CLI_DESCRIPTION: str = "Generate a Forge edition to code map by scanning Forge edition files."
CLI_EPILOG: str = "Examples:\n  %(prog)s\n  %(prog)s -s auto\n  %(prog)s -s fast\n  %(prog)s -s full"

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    """
    Generate the Forge to edition code map.

    Builds a mapping of edition codes to Forge edition names by scanning
    Forge edition files.
    """    
    try:
        runtime.initialize_runtime(LOG_NAME)    
        cli_args = parse_cli_args()
        apply_cli_args(cli_args)

        edition_code_map: DataMap = DataMap(
            display_name=data_map_const.FORGE_EDITION_TO_CODE_MAP_DISPLAY_NAME,
            map_key=data_map_const.FORGE_EDITION_TO_CODE_MAP_KEY,
            version=data_map_const.FORGE_EDITION_TO_CODE_MAP_VERSION
        )
        
        logger.info("Iterating Forge editions directory to Forge edition to code map...")
        for file in paths.get_forge_editions_dir().glob(f"*.{path_const.FILE_EXTENSION_FORGE_EDITION}"):
            edition_name: str = file.stem
            edition_code: str = extract_edition_code(file)

            if edition_code is None:
                continue
            if edition_name in edition_code_map:
                logger.error(
                    "Unable to resolve duplicate edition code ('%s') between editions: '%s', '%s'.",
                    edition_code,
                    edition_code_map[edition_code],
                    edition_name
                )
                sys.exit(1)

            edition_code_map[edition_name] = edition_code

        logger.info("Mapped %d editions.", len(edition_code_map))
        edition_code_map.persist_to(paths.build_forge_edition_to_code_map_path())
        logger.info("Compilation complete!")
    except Exception:
        log_utils.log_unexpected_and_exit()

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================
def parse_cli_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the CLI.

    Returns:
        An argparse.Namespace containing encoding scan options.
    """        
    parser = argparse.ArgumentParser(
        prog=CLI_PROG,
        description=CLI_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    args.add_encoding_scan_mode_argument(parser)

    return parser.parse_args()

def apply_cli_args(args: argparse.Namespace) -> None:
    """
    Apply command-line arguments on top of the loaded configuration.

    CLI arguments take precedence over config.toml values. Only applies
    arguments that were explicitly provided by the user, mutating the
    provided configuration object in place.

    Args:
        args: The parsed command-line arguments.
    """  
    if args.encoding_scan is not None:
        settings.set_encoding_scan_mode(EncodingScanMode(args.encoding_scan))      


def extract_edition_code(edition_file: Path) -> str | None:
    """
    Read the Forge edition code from a Forge edition file.

    The Forge edition code is defined by the edition's standard Code and
    is used as the edition's primary identifier.

    Args:
        edition_file: The path to the edition to read.

    Returns:
        The Forge edition code associated with the edition or None if
        no edition code exists.
    """    
    forge_edition_code: str | None = file_utils.read_text_field(
        file_path=edition_file,
        field_prefix=forge_const.FORGE_EDITION_CODE_PREFIX,
        encoding_full_scan=settings.get_encoding_full_scan())

    if forge_edition_code is None:
        logger.warning("Unable to extract edition code from edition '%s'.", edition_file.stem)

    return forge_edition_code

if __name__ == "__main__":
    main()