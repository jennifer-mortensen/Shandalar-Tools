"""
Validate Shandalar edition mappings.

Ensures that every Forge edition referenced by the Shandalar
edition map exists as a Forge edition file. Reports any invalid
mappings found during validation.
"""
from common import args, args_types, log_utils, runtime, settings
from common.args_types import CliDefinition
from mtg import forge_data
from resources import data_map_loader
from resources.data_map import DataMap
import logging
import sys

logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
LOG_NAME: str = "edition_map_validator"

CLI_DEFINITION: CliDefinition = CliDefinition(
    prog="edition-map-validator",
    description="Validate the contents of a Shandalar edition map against existing Forge edition files.",
    epilog=(
        "Examples:\n"
        "  %(prog)s\n"
        "  %(prog)s -d shandalar_2016"
    ),
    arguments = (
        # Common
        args_types.ARGUMENT_ENCODING_SCAN_MODE,
        args_types.ARGUMENT_LOG_FILE_NAME,
        args_types.ARGUMENT_LOG_OVERWRITE,
        args_types.ARGUMENT_LOG_PREVIEW_LIMIT,
        args_types.ARGUMENT_SHANDALAR_DATASET
    )
)
# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    """
    Validate the Shandalar edition map.

    Loads the active Shandalar edition map and verifies that every
    mapped Forge edition exists.

    Any invalid mappings are logged as errors. A success message is
    logged if all mappings are valid.
    """ 
    try:
        runtime.initialize_runtime(LOG_NAME)
        args.process_cli_args(CLI_DEFINITION) 

        edition_validation_cache: dict[str, bool] = {}
        shandalar_edition_map: DataMap | None = (data_map_loader.get_shandalar_to_forge_edition_map(settings.get_shandalar_dataset()))

        if shandalar_edition_map is None:
            logger.error("Requested edition map could not be loaded. Program will now terminate.")
            sys.exit(1)
        
        invalid_mappings: list[str] = []

        logger.info("Validating %d Shandalar edition mappings against Forge edition files...", len(shandalar_edition_map))

        for shandalar_edition, forge_edition in shandalar_edition_map.items():
            key_val_pair: str = f"{shandalar_edition} -> {forge_edition}"
            forge_edition_is_valid: bool | None = edition_validation_cache.get(forge_edition)
            
            if forge_edition_is_valid is None:
                forge_edition_is_valid = forge_data.edition_exists(forge_edition)
                edition_validation_cache[forge_edition] = forge_edition_is_valid    

            if forge_edition_is_valid:
                logger.debug("Validation passed: %s", key_val_pair)
            else:
                invalid_mappings.append(key_val_pair)
                logger.debug("Validation failed: %s", key_val_pair)

        if invalid_mappings:
            invalid_keys_display: str = "\n  ".join(invalid_mappings)
            logger.error("Validation failed. Invalid Shandalar -> Forge edition mappings:\n  %s", invalid_keys_display)
        else:
            logger.info("Validation passed.")

        runtime.terminate_resources()

    except Exception:
        log_utils.log_unexpected_and_exit()

if __name__ == "__main__":
    main()