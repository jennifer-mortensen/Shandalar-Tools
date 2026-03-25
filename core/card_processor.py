from core import card_loader, const
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATA CONSTRUCTION
# ==============================

# Returns a set containing all cards from the given editions.
def get_card_pool(editions) -> set[str]:
    editions_loaded = set()
    cards = set()

    for e in editions:
        logger.info(f"Loading {e}...")
        sanitized_edition_name = card_loader.sanitize_name(e)
        if sanitized_edition_name in editions_loaded:
            logger.warning(f"Duplicate detected. Skipping {e}.")
            continue

        edition_cards = card_loader.get_edition_cards(e)
        cards.update(edition_cards)
        editions_loaded.add(sanitized_edition_name)

    return cards

# Returns a set of edition codes for the given editions list.
def generate_edition_codes(editions) -> set[str]:
    # TODO: filter out duplicates earlier in the pipeline
    logger.info("Generating edition codes...")
    edition_codes = set()

    for e in editions:
        code = card_loader.get_edition_code(e)
        edition_codes.add(code)

    return edition_codes

# ==============================
# DATA TRANSFORMATION
# ==============================

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def get_unsupported_cards(cards, shandalar_lookup) -> list[str]:
    unsupported_cards = [c for c in cards if card_loader.sanitize_name(c) not in shandalar_lookup]
    logger.info(f"Found {len(unsupported_cards)} unsupported cards.")
    
    return unsupported_cards

# ==============================
# OUTPUT FORMATTING
# ==============================

# Formats output for the MTG Forge format.
def generate_forge_format(cards, user_banned_cards, edition_codes, sort_cards=True) -> str:
    # Base list (sorted for readability if enabled)
    formatted_cards = sorted(cards) if sort_cards else list(cards)

    # Append user-banned cards without altering order or removing duplicates
    for c in user_banned_cards or []:
        if c not in cards:
            formatted_cards.append(c)

    # Warn about duplicates in user list
    if user_banned_cards:
        seen = set()
        duplicates = set()

        for c in user_banned_cards:
            if c in seen:
                duplicates.add(c)
            seen.add(c)

        if duplicates:
            duplicates_list = sorted(duplicates)
            preview = ", ".join(duplicates_list[:5])

            logger.warning(
                f"{len(duplicates)} duplicate entries detected "
                f"in user-banned list (preserved as-is). "
                f"Examples: {preview}"
                + ("..." if len(duplicates) > const.PREVIEW_LIMIT else "")
            )

    banned_cards = "; ".join(formatted_cards)
    set_codes = ", ".join(edition_codes)

    forge_format = const.FORGE_FORMAT_BODY_STANDARD.format(
        banned_cards=banned_cards,
        set_codes=set_codes
    )

    if not forge_format:
        # If we're here, we've probably encountered a bug.
        raise ValueError("Failed to generate MTG: Forge format output.")

    return forge_format

# ==============================
# HELPERS
# ==============================

# Returns a sanitized set of shandalar cards for comparison.
def build_shandalar_lookup() -> set[str]:
    return card_loader.sanitize_set(card_loader.get_shandalar_cards())