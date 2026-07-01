"""
Validate Shandalar edition mappings.

Ensures that every Forge edition referenced by the Shandalar
edition map exists as a Forge edition file. Reports any invalid
mappings found during validation.
"""
from resources import data_map_loader
from resources.data_map import DataMap
from common import log_utils, runtime
from mtg import forge_data
import argparse
import logging
import sys


logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
MODULE_NAME: str = "edition_map_validator"
LOG_NAME: str = MODULE_NAME
CLI_PROG: str = "edition-map-validator"
CLI_DESCRIPTION: str = "Validate the contents of a Shandalar edition map against existing Forge edition files."
CLI_EPILOG: str = "Examples:\n  %(prog)s\n  %(prog)s -d shandalar_2016"

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

        args = parse_cli_args()
        edition_validation_cache: dict[str, bool] = {}
        shandalar_edition_map: DataMap | None = data_map_loader.get_shandalar_to_forge_edition_map(args.dataset)

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

    except Exception:
        log_utils.log_unexpected_and_exit()

def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=CLI_PROG,
        description=CLI_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-d", "--dataset",
        help="The dataset to validate the edition map for. Validates the default map if not specified."
    )

    return parser.parse_args()        

if __name__ == "__main__":
    main()