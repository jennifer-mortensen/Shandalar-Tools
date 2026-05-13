import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import common_const, file_utils
from common.common_const import EncodingScanMode
from config import config_io, runtime
from config.format_generator_config import FormatGeneratorConfig
from format_generator import format_const, format_pipeline
from format_generator.format_const import ForgeFormatInput, ForgeFormatOutput
import argparse
import logging

logger = logging.getLogger(__name__)

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    try:
        runtime.initialize_runtime()

        cli_args = parse_cli_args()
        if not validate_cli_args(cli_args):
            sys.exit(1)

        format_config = config_io.build_format_generator_config()
        format_config = apply_cli_args(args=cli_args, config=format_config)

        input_format: ForgeFormatInput = format_pipeline.build_input_format(format_pipeline.get_input_format_path(format_config.input_format_file))
        output_format: ForgeFormatOutput = format_pipeline.build_output_format(input_format=input_format, config=format_config)
        format_pipeline.write_output_format(output_format)

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
        "-o", "--output-format",
        choices=format_const.FORGE_FORMAT_VALID_VALUES,
        help="Forge format type to be generated.",
    )
    parser.add_argument(
        "-e", "--editions",
        action="store_true",
        default=False,
        help="Deprecated. --editions and --user-banned are no longer supported. Format specification has moved to a single .toml file. See the readme for migration details."
    )
    parser.add_argument(
        "-b", "--user-banned",
        action="store_true",
        default=False,
        help="Deprecated. --editions and --user-banned are no longer supported. Format specification has moved to a single .toml file. See the readme for migration details."
    )    
    parser.add_argument(
        "-i", "--input-file",
        type=lambda file_name: file_utils.ensure_extension(
            file_path=common_const.FORMATS_DIR / Path(file_name),
            extension=format_const.FILE_TYPE_INPUT_FORMAT
        ),
        help="TOML file describing the format to be generated.",
    )
    parser.add_argument(
        "-s", "--encoding-scan",
        choices=common_const.ENCODING_SCAN_VALID_VALUES,
        help=(
            "Encoding detection mode: "
            "auto (use built-in defaults), "
            "fast (partial read, faster but may miss issues), "
            "full (scan entire file, slower but reliable)."
        )
    )

    return parser.parse_args()

def validate_cli_args(args: argparse.Namespace) -> bool:
    """
    Validate command-line arguments for deprecated flags.

    Logs an error and returns False if any deprecated arguments are detected.

    Args:
        args: The parsed command-line arguments.
    """    
    if args.editions or args.user_banned:
        logger.error("--editions and --user-banned are no longer supported. Format specification has moved to a single .toml file. See the readme for migration details.")
        return False
    return True

def apply_cli_args(args: argparse.Namespace, config: FormatGeneratorConfig) -> FormatGeneratorConfig:
    """
    Apply command-line arguments on top of the loaded configuration.

    CLI arguments take precedence over config.toml values. Only applies
    arguments that were explicitly provided by the user.

    Args:
        args: The parsed command-line arguments.
        config: The configuration object to update.
    """    
    if args.encoding_scan is not None:
        runtime.set_encoding_scan_mode(EncodingScanMode(args.encoding_scan))
    if args.input_file is not None:
        config.input_format_file = args.input_file
    if args.output_format is not None:
        config.output_format_type = format_const.parse_forge_format(args.output_format)

    return config

if __name__ == "__main__":
    main()