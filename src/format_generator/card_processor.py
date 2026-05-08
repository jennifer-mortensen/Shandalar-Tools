"""
Card data processing for Shandalar Tools format generator.

Provides functions for building card pools from Forge edition files,
constructing the Shandalar card lookup, collecting Scryfall edition
codes, and identifying unsupported cards.
"""
from common import common_utils
from config.format_generator_config import FormatGeneratorConfig
from format_generator import card_loader

import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC_FUNCTIONS
# ==============================
def build_format_card_pool(edition_names: list[str], config: FormatGeneratorConfig) -> set[str]:
    """
    Build a set of card names from the specified Forge editions.

    Loads each edition in order, skipping duplicates. Logs a warning
    for any duplicate edition names detected.

    Args:
        edition_names: Names of the editions to load.
        config: Configuration controlling encoding scan behavior.
    """    
    logger.info("Building card pool from editions...")    
    editions_loaded: set[str] = set()
    cards: set[str] = set()

    for e in edition_names:
        sanitized_edition_name: str = common_utils.sanitize_name(e)
        if sanitized_edition_name in editions_loaded:
            logger.warning("Duplicate edition '%s' detected; skipping.", e)
            continue

        logger.debug("Loading edition '%s'...", e)

        cards.update(card_loader.get_edition_card_names(edition_name=e, config=config))
        editions_loaded.add(sanitized_edition_name)

    return cards

def build_shandalar_card_lookup(config: FormatGeneratorConfig) -> set[str]:
    """
    Build a sanitized set of Shandalar card names for lookup.

    Reads the Shandalar card data file and returns a set of sanitized
    card names suitable for case-insensitive comparison.

    Args:
        config: Configuration controlling encoding scan behavior.
    """    
    logger.info("Loading Shandalar card pool...")
    return common_utils.sanitize_set(card_loader.get_shandalar_card_names(config))

def collect_scryfall_codes(edition_names: list[str], config: FormatGeneratorConfig) -> set[str]:
    """
    Collect Scryfall edition codes for a list of edition names.

    Args:
        edition_names: Names of the editions to collect codes for.
        config: Configuration controlling encoding scan behavior.
    """    
    logger.info("Generating Scryfall edition codes...")
    
    scryfall_codes: set[str] = set()

    for e in edition_names:
        logger.debug("Collecting scryfall code for '%s'...", e)
        code = card_loader.get_scryfall_code(edition_name=e, config=config)
        scryfall_codes.add(code)

    return scryfall_codes

def find_unsupported_in_shandalar(card_names: set[str], shandalar_lookup: set[str]) -> list[str]:
    """
    Identify cards that are not supported by Shandalar.

    Compares card names against the Shandalar lookup using sanitized
    comparison. Returns a list of unsupported card names in their
    original unsanitized form.

    Args:
        card_names: The set of card names to check.
        shandalar_lookup: A sanitized set of Shandalar supported card names.
    """    
    unsupported_card_names: list[str] = [c for c in card_names if common_utils.sanitize_name(c) not in shandalar_lookup]
    logger.info("Identified %d unsupported cards.", len(unsupported_card_names))
    
    return unsupported_card_names