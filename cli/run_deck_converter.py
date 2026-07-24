"""
Command-line entry point for the Shandalar Tools deck converter.

Initializes shared runtime services, loads configuration, applies
command-line overrides, and executes deck conversion between
supported deck formats.
"""
import sys
from pathlib import Path

from deck_converter import deck_converter_const
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common import args, log_utils, runtime
from deck_converter import deck_converter_pipeline
import logging

logger = logging.getLogger(__name__)

def main() -> None:
    """
    Execute the deck converter command-line application.

    Initializes runtime services, processes command-line arguments,
    executes the deck conversion pipeline, and reports any
    unexpected errors.
    """
    try:
        runtime.initialize_runtime(deck_converter_const.LOG_NAME)
        args.process_cli_args(deck_converter_const.CLI_DEFINITION)
        deck_converter_pipeline.run_pipeline()
        logger.info("Deck conversion complete!")
    except Exception:
        log_utils.log_unexpected_and_exit()

if __name__ == "__main__":
    main()