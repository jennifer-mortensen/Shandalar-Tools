"""
Command-line entry point for the Shandalar Tools format builder.

Initializes shared runtime services, loads configuration, applies
command-line overrides, and generates Forge format files from
user-supplied format specifications.
"""
import sys
from pathlib import Path

from format_builder import format_builder_const
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import args, log_utils, paths, runtime, settings
from format_builder import format_builder_pipeline
from format_builder.format_builder_types import ForgeFormatInput, ForgeFormatOutput
import argparse
import logging

logger = logging.getLogger(__name__)

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    try:
        runtime.initialize_runtime(format_builder_const.LOG_NAME)
        args.process_cli_args(format_builder_const.CLI_DEFINITION)

        input_format: ForgeFormatInput = format_builder_pipeline.build_input_format(
            paths.build_format_config_path(settings.get_format_config_file_name())
        )
        output_format: ForgeFormatOutput = format_builder_pipeline.build_output_format(input_format)
        format_builder_pipeline.write_output_format(output_format)

        logger.info("Compilation completed successfully!")
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception:
        log_utils.log_unexpected_and_exit()

if __name__ == "__main__":
    main()