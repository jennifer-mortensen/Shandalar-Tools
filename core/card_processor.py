from core import card_loader, const
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATA CONSTRUCTION
# ==============================

# Returns a set containing all cards from the given editions.
def build_card_pool(editions: list[str]) -> set[str]:
    editions_loaded = set()
    cards = set()

    for e in editions:
        logger.info("Loading edition '%s'...", e)
        sanitized_edition_name = card_loader.sanitize_name(e)
        if sanitized_edition_name in editions_loaded:
            logger.warning("Duplicate edition '%s' detected; skipping.", e)
            continue

        edition_cards = card_loader.get_edition_cards(e)
        cards.update(edition_cards)
        editions_loaded.add(sanitized_edition_name)

    return cards

# Returns a set of edition codes for the given editions list.
def collect_edition_codes(editions: list[str]) -> set[str]:
    # TODO: filter out duplicates earlier in the pipeline
    logger.info("Generating Scryfall edition codes...")
    edition_codes = set()

    for e in editions:
        code = card_loader.get_edition_code(e)
        edition_codes.add(code)

    return edition_codes

# ==============================
# DATA TRANSFORMATION
# ==============================

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def find_unsupported_cards(cards: set[str], shandalar_lookup: set[str]) -> list[str]:
    unsupported_cards = [c for c in cards if card_loader.sanitize_name(c) not in shandalar_lookup]
    logger.info("Identified %d unsupported cards.", len(unsupported_cards))
    
    return unsupported_cards

# ==============================
# OUTPUT FORMATTING
# ==============================

# Formats output for the MTG Forge format.
def build_forge_format(cards: list[str], user_banned_cards: list[str], edition_codes: set[str], sort_cards: bool = True) -> str:
    # Base list (sorted for readability if enabled)
    formatted_cards = sorted(cards) if sort_cards else list(cards)
    seen = set()
    duplicates = set()

    # Append user-banned cards without altering order or removing duplicates
    for c in user_banned_cards:
        if c not in cards:
            formatted_cards.append(c)
        if c in seen:
            duplicates.add(c)
        else:
            seen.add(c)            

    # Warn about duplicates in user list
    if duplicates:
        duplicates_list = sorted(duplicates)
        preview = ", ".join(duplicates_list[:const.PREVIEW_LIMIT])
        logger.warning(
            "%d duplicate entries detected in the user-banned list (preserved as-is). "
            "Examples: %s%s\nFull details written to the log file (default: %s)",
            len(duplicates),
            preview,
            "..." if len(duplicates) > const.PREVIEW_LIMIT else "",
            card_loader.normalize_filename(const.FILE_NAME_LOG, const.FILE_TYPE_LOG)
        )
        logger.debug("Duplicate entries: %s", duplicates_list)

    banned_cards = "; ".join(formatted_cards)
    set_codes = ", ".join(edition_codes)

    forge_format = const.FORGE_FORMAT_BODY_STANDARD.format(
        banned_cards=banned_cards,
        set_codes=set_codes
    )

    if not forge_format:
        # Sanity check: if we're here, we've probably encountered a bug.
        raise ValueError("Failed to generate MTG: Forge format output.")

    return forge_format

# ==============================
# HELPERS
# ==============================

# Returns a sanitized set of shandalar cards for comparison.
def build_shandalar_card_lookup() -> set[str]:
    return card_loader.sanitize_card_set(card_loader.get_shandalar_cards())