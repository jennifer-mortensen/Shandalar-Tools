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

from common import args, log_utils, runtime
from format_builder import format_builder_pipeline
import logging

logger = logging.getLogger(__name__)

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    """
    Execute the format builder command-line application.

    Initializes runtime services, processes command-line arguments,
    executes the format generation pipeline, and reports any
    unexpected errors.
    """    
    try:
        runtime.initialize_runtime(format_builder_const.LOG_NAME)
        args.process_cli_args(format_builder_const.CLI_DEFINITION)
        format_builder_pipeline.run_pipeline()
        logger.info("Format generation complete!")
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception:
        log_utils.log_unexpected_and_exit()

if __name__ == "__main__":
    main()