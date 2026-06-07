"""
Command-line entry point for the Shandalar Tools format generator.

Initializes shared runtime services, loads configuration, applies
command-line overrides, and generates Forge format files from
user-supplied format specifications.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import args_utils, common_args, log_utils, path_utils, runtime
from common.common_types import EncodingScanMode
from config import config_io
from config.format_generator_config import FormatGeneratorConfig
from pipeline import format_generator_const, format_generator_pipeline, format_generator_types
from pipeline.format_generator_types import ForgeFormatInput, ForgeFormatOutput
import argparse
import logging

logger = logging.getLogger(__name__)

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    try:
        runtime.initialize_runtime(format_generator_const.LOG_NAME)

        cli_args = parse_cli_args()
        validate_cli_args(cli_args)

        config = config_io.build_format_generator_config()
        apply_cli_args(args=cli_args, config=config)

        input_format: ForgeFormatInput = format_generator_pipeline.build_input_format(path_utils.build_format_config_path(config.format_config_file))
        output_format: ForgeFormatOutput = format_generator_pipeline.build_output_format(input_format=input_format, config=config)
        format_generator_pipeline.write_output_format(output_format)

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
        prog=format_generator_const.CLI_PROG,
        description=format_generator_const.CLI_DESCRIPTION,
        epilog=format_generator_const.CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )    
    parser.add_argument(
        "-o", "--output-format",
        choices=format_generator_types.FORGE_FORMAT_VALID_VALUES,
        help="Forge format type to be generated.",
    )
    parser.add_argument(
        "-i", "--input-file",
        type=path_utils.build_format_config_path,
        help="TOML file describing the format to be generated.",
    )
    for argument in format_generator_const.DEPRECATED_ARGUMENTS:
        parser.add_argument(
            argument.short_name,
            argument.long_name,
            action="store_true",
            default=False,
            help=args_utils.build_deprecated_arg_message(argument)
        )
    common_args.add_encoding_scan_argument(parser)

    return parser.parse_args()

def validate_cli_args(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments for deprecated or unsupported options.

    Raises a ValueError if invalid or deprecated arguments are detected.

    Args:
        args: The parsed command-line arguments.

    Raises:
        ValueError: If deprecated or unsupported arguments are provided.
    """
    if args_utils.has_any_arg(source_args=args, cli_arguments=format_generator_const.DEPRECATED_ARGUMENTS):
        raise ValueError(format_generator_const.ERROR_DEPRECATED_ARGUMENTS)

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
        config.output_format_type = format_generator_types.parse_forge_format(args.output_format)

if __name__ == "__main__":
    main()