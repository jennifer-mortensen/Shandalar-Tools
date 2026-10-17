"""
Generate a Shandalar edition map from the active card pool.

Builds a dataset-specific edition map by extracting unique
edition names from the active Shandalar card pool and
attempting to resolve them to Forge edition names. Editions
that cannot be resolved automatically are marked for manual
review.
"""
from common import args, args_types, log_utils, paths, runtime, settings, string_utils
from common.args_types import CliDefinition
from mtg import forge_data
from resources import data_map_const, data_map_loader, lookup_loader
from resources.data_map import DataMap
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
LOG_NAME: str = "shandalar_edition_map_generator"

CLI_DEFINITION: CliDefinition = CliDefinition(
    prog="shandalar-edition-map-generator",
    description="Generate Shandalar edition to Forge edition map by resolving editions from the Shandalar card pool.",
    epilog=(
        "Examples:\n"
        "  %(prog)s\n"
        "  %(prog)s -s auto\n"
        "  %(prog)s -s fast\n  "
        "  %(prog)s -s full"
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
        args.process_cli_args(CLI_DEFINITION)

        dataset: str = settings.get_shandalar_dataset()
        shandalar_lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)
        edition_map: DataMap = data_map_loader.create_shandalar_to_forge_edition_map(register=False)

        logger.info("Collecting editions from dataset '%s'...", dataset)
        for card in shandalar_lookup.values():
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