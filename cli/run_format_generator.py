import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import common_args, common_const, file_utils, log_utils
from common.common_types import EncodingScanMode
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
        validate_cli_args(cli_args)

        format_config = config_io.build_format_generator_config()
        apply_cli_args(args=cli_args, config=format_config)

        input_format: ForgeFormatInput = format_pipeline.build_input_format(format_pipeline.get_input_format_path(format_config.input_format_file))
        output_format: ForgeFormatOutput = format_pipeline.build_output_format(input_format=input_format, config=format_config)
        format_pipeline.write_output_format(output_format)

        logger.info("Compilation completed successfully!")
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception:
        log_utils.log_unexpected_and_exit()

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
        prog="format-generator",
        description="Generate Shandalar-compatible formats for use with MTG: Forge.",
        epilog=(
            "Examples:\n"
            "  %(prog)s\n"
            "  %(prog)s -i my_format.toml\n"
            "  %(prog)s -o modern\n"
            "  %(prog)s -s full"
        ),
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
            file_path=common_const.INPUT_FORMAT_DIR / Path(file_name),
            extension=format_const.FILE_TYPE_INPUT_FORMAT
        ),
        help="TOML file describing the format to be generated.",
    )
    common_args.add_encoding_scan_argument(parser)

    return parser.parse_args()

def validate_cli_args(args: argparse.Namespace):
    """
    Validate command-line arguments for deprecated or unsupported options.

    Raises a ValueError if invalid or deprecated arguments are detected.

    Args:
        args: The parsed command-line arguments.

    Raises:
        ValueError: If deprecated or unsupported arguments are provided.
    """   
    if args.editions or args.user_banned:
        raise ValueError("--editions and --user-banned are no longer supported. Format specification has moved to a single .toml file. See the readme for migration details.")

def apply_cli_args(args: argparse.Namespace, config: FormatGeneratorConfig) -> None:
    """
    Apply command-line arguments on top of the loaded configuration.

    CLI arguments take precedence over config.toml values. Only applies
    arguments that were explicitly provided by the user, mutating the
    provided configuration object in place.

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

if __name__ == "__main__":
    main()