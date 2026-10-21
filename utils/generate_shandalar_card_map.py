"""
Validate and repair Shandalar card-to-Forge edition references.

Validates the Forge edition reference for each card in the configured
Shandalar dataset and attempts to remap any broken references.
"""
from common import args, args_types, runtime, settings, string_utils
from common.args_types import CliDefinition
from mtg import mtg_data
from resources import lookup_loader
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

# ==============================
# CONSTANTS
# ==============================
LOG_NAME: str = "shandalar_card_map_generator"

CLI_DEFINITION: CliDefinition = CliDefinition(
    prog="shandalar-card-map-generator",
    description="Validate and repair Shandalar card to Forge edition references.",
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

# ==============================
# MAIN ENTRY POINT
# ==============================
def main() -> None:
    """
    Validate and repair card-to-Forge edition references.

    Loads the configured Shandalar dataset, validates each card's
    existing Forge edition reference, and attempts to create a new
    reference for any broken mappings. Logs a summary of the validation
    and repair results.
    """    
    runtime.initialize_runtime(LOG_NAME)
    args.process_cli_args(CLI_DEFINITION)    

    dataset: str = settings.get_shandalar_dataset()

    shandalar_lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)
    broken_reference_count: int = 0
    mapped_reference_count: int = 0

    logger.info("Validating references...")

    for card in shandalar_lookup.values():
        if not mtg_data.validate_card_reference(card.id, dataset):
            logger.info("Detected broken reference for card: Shandalar ID '%s', Normalized Name '%s'", card.id, card.normalized_name)
            if mtg_data.map_card(card.id, dataset):
                mapped_reference_count += 1
            broken_reference_count += 1

    if not broken_reference_count:
        logger.info(
            "%s references successfully validated!", 
            string_utils.pluralize(quantity=len(shandalar_lookup), singular="reference", plural="references")
        )
    else:
        logger.info(
            "Found %d broken %s in dataset '%s'. Successfully resolved %s of them.",
            broken_reference_count,            
            string_utils.pluralize(quantity=broken_reference_count, singular="reference", plural="references"),
            dataset if dataset is not None else "default",
            "all" if broken_reference_count == mapped_reference_count else "none" if not mapped_reference_count else str(mapped_reference_count)
        )

    runtime.terminate_resources()

if __name__ == "__main__":
    main()
