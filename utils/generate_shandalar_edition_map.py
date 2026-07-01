"""
Generate a Shandalar edition map from the active card pool.

Builds a dataset-specific edition map by extracting unique
edition names from the active Shandalar card pool and
attempting to resolve them to Forge edition names. Editions
that cannot be resolved automatically are marked for manual
review.
"""
from common import log_utils, paths, runtime, settings, string_utils
from mtg import forge_data
from resources import data_map_const, lookup_loader
from resources.data_map import DataMap
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
LOG_NAME: str = "shandalar_edition_map_generator"
UNRESOLVED_EDITION_FLAG: str = "[UNRESOLVED EDITION]"

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    """
    Generate a Shandalar edition map for the active dataset.

    Extracts all unique Shandalar editions, resolves editions
    that exactly match Forge edition names, reports generation
    statistics, and writes the resulting edition map to disk.
    """    
    try:
        runtime.initialize_runtime(LOG_NAME)

        dataset: str = settings.get_shandalar_dataset()
        shandalar_lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup()
        edition_map: DataMap = DataMap(
            display_name=data_map_const.SHANDALAR_TO_FORGE_EDITION_MAP_DISPLAY_NAME,
            map_key=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_KEY,
            version=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_VERSION
        )

        logger.info("Collecting editions from dataset '%s'...", dataset)
        for card in shandalar_lookup.cards.values():
            if card.edition in edition_map:
                continue

            forge_edition: str = card.edition if forge_data.edition_exists(card.edition) else UNRESOLVED_EDITION_FLAG
            edition_map[card.edition] = forge_edition

        log_edition_map_results(edition_map)
        edition_map.persist_to(paths.build_shandalar_to_forge_edition_map_file_path(dataset))
        logger.info("Compilation complete!")
    except Exception:
        log_utils.log_unexpected_and_exit()

# ==============================
# HIGH LEVEL FUNCTIONS
# ==============================
def log_edition_map_results(edition_map: DataMap) -> None:
    """
    Log summary statistics for a generated edition map.

    Reports the total number of discovered Shandalar editions,
    the number automatically resolved to Forge editions, and
    the number requiring manual review.

    Args:
        edition_map: The generated edition map.
    """    
    edition_count: int = len(edition_map)
    auto_resolved_count: int = sum(value != UNRESOLVED_EDITION_FLAG for value in edition_map.values())
    unresolved_count: int = edition_count - auto_resolved_count

    requires_pluralized: str = string_utils.pluralize(quantity=unresolved_count, singular="requires", plural="require")
    unresolved_message: str = f" {unresolved_count} {requires_pluralized} manual review." if unresolved_count > 0 else ""
    message: str = f"Auto-resolved {auto_resolved_count}/{edition_count} editions.{unresolved_message}"

    logger.info(message)

if __name__ == "__main__":
    main()