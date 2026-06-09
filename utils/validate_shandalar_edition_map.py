"""
Validate Shandalar edition mappings.

Ensures that every edition code referenced by the Shandalar edition
map exists as a key in the Forge Scryfall map. Reports any invalid
mappings found during validation.
"""
from common import log_utils, runtime
from mtg import forge_data, shandalar_data
import logging

logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
LOG_NAME: str = "shandalar_map_validator"

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    """
    Validate the Shandalar edition map.

    Loads the Forge Scryfall map and Shandalar edition map, then verifies
    that every edition code referenced by the Shandalar map exists in the
    Forge Scryfall map.

    Any invalid mappings are logged as errors. A success message is logged
    if all mappings are valid.
    """    
    try:
        runtime.initialize_runtime(LOG_NAME)    
        
        forge_scryfall_map: dict[str, str] = forge_data.read_forge_scryfall_map()
        shandalar_edition_map: dict[str, str] = shandalar_data.read_shandalar_edition_map()
        invalid_keys: list[str] = []

        logger.info("Validating Shandalar edition map against Forge Scryfall map...")
        for shandalar_key, shandalar_val in shandalar_edition_map.items():
            key_val_pair: str = f"{shandalar_key} -> {shandalar_val}"
            # Every Shandalar edition map value should resolve to a key in the Forge Scryfall map.        
            if shandalar_val not in forge_scryfall_map:
                logger.debug("Validation failed: %s", key_val_pair)
                invalid_keys.append(key_val_pair)
            else:
                logger.debug("Validation passed: %s", key_val_pair)

        if invalid_keys:
            invalid_keys_display: str = "\n  ".join(invalid_keys)
            logger.error("Validation failed. Invalid Shandalar edition mappings:\n  %s", invalid_keys_display)
        else:
            logger.info("Validation passed.")
    except Exception:
        log_utils.log_unexpected_and_exit()

if __name__ == "__main__":
    main()