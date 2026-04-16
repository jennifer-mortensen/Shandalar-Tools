from collections.abc import Iterable, Sequence
from core import card_loader, const
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATA CONSTRUCTION
# ==============================

def build_card_pool(editions: Sequence[str]) -> set[str]:
    """
    Build and return a set of all cards from the specified editions.

    Duplicate edition names are ignored. A warning is logged when
    duplicates are encountered.

    Args:
        editions: A sequence of edition names to load.

    Returns:
        A set containing all unique card names from the given editions.
    """    
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

def collect_edition_codes(editions: Sequence[str]) -> set[str]:
    """
    Generate Scryfall edition codes for the provided editions.

    Args:
        editions: A sequence of edition names.

    Returns:
        A set of Scryfall edition codes.
    """    
    logger.info("Generating Scryfall edition codes...")
    edition_codes = set()

    for e in editions:
        code = card_loader.get_edition_code(e)
        edition_codes.add(code)

    return edition_codes

# ==============================
# DATA TRANSFORMATION
# ==============================

def find_duplicates(card_lists: Iterable[Iterable[str]]) -> list[str]:
    """
    Identify duplicate entries within or across multiple iterables.

    Args:
        card_lists: An iterable containing iterables of card names.

    Returns:
        A sorted list of unique duplicate card names.
    """    
    seen = set()
    duplicates = set()

    for card_list in card_lists:
        for card in card_list:
            if card in seen:
                duplicates.add(card)
            else:
                seen.add(card)

    return sorted(duplicates)   

def find_unsupported_cards(cards: set[str], shandalar_lookup: set[str]) -> list[str]:
    """
    Determine which cards are unsupported by Shandalar.

    Args:
        cards: A set of card names to evaluate.
        shandalar_lookup: A sanitized set of supported Shandalar card names.

    Returns:
        A list of card names not supported by Shandalar.
    """    
    unsupported_cards = [c for c in cards if card_loader.sanitize_name(c) not in shandalar_lookup]
    logger.info("Identified %d unsupported cards.", len(unsupported_cards))
    
    return unsupported_cards

def merge_and_dedupe_sequences(seq_1: Sequence[str], seq_2: Sequence[str]) -> list[str]:
    """
    Merge two sequences while preserving order and preventing duplicates.

    A new list is returned containing all elements from ``seq_1`` followed
    by elements from ``seq_2`` that are not already present. The original
    input sequences are not modified.

    Args:
        seq_1: The base sequence whose elements appear first in the result.
        seq_2: The sequence whose unique elements will be appended.

    Returns:
        A new list containing unique elements from both sequences, with
        the original ordering preserved.
    """
    merged = list(seq_1)
    seen = set(merged)

    for item in seq_2:
        if item not in seen:
            merged.append(item)
            seen.add(item)

    return merged

# ==============================
# OUTPUT FORMATTING
# ==============================

def build_forge_format(cards: Sequence[str], user_banned_cards: Sequence[str], edition_codes: set[str], sort_cards: bool = True) -> str:
    """
    Generate a valid MTG: Forge format string.

    The function combines unsupported cards with user-defined banned
    cards, logs duplicate entries across both lists, and formats the
    result according to the Forge specification.

    Args:
        cards: A sequence of unsupported card names.
        user_banned_cards: A sequence of user-specified banned cards.
        edition_codes: A set of Scryfall edition codes.
        sort_cards: Whether to sort unsupported cards for readability.

    Returns:
        A formatted MTG: Forge configuration string.

    Raises:
        AssertionError: If the Forge format string cannot be generated,
            indicating an upstream logic error.
    """    
    # Base list (sorted for readability if enabled).
    formatted_cards = sorted(cards) if sort_cards else list(cards)

    # Log duplicates between lists.
    log_duplicates(find_duplicates([formatted_cards, user_banned_cards]))

    banned_cards = "; ".join(merge_and_dedupe_sequences(formatted_cards, user_banned_cards))
    set_codes = ", ".join(sorted(edition_codes))

    forge_format = const.FORGE_FORMAT_BODY_STANDARD.format(
        banned_cards=banned_cards,
        set_codes=set_codes
    )

    assert forge_format, "Expected a valid forge_format string from build_forge_format(). Check recent changes upstream."

    return forge_format

# ==============================
# HELPERS
# ==============================

def build_shandalar_card_lookup() -> set[str]:
    """
    Build a sanitized lookup set of Shandalar-supported card names.

    Returns:
        A lowercase, trimmed set of supported card names.
    """    
    return card_loader.sanitize_card_set(card_loader.get_shandalar_cards())      

def log_duplicates(duplicates: list[str]) -> None:
    """
    Log duplicate card entries detected across input lists.

    A preview is shown in the CLI, while the full list is written
    to the debug log.

    Args:
        duplicates: A sorted list of duplicate card names.
    """    
    if duplicates:
        preview = ", ".join(duplicates[:const.PREVIEW_LIMIT])
        logger.warning(
            "%d duplicate card entries detected across the unsupported and user-banned lists "
            "(preserved as-is). Examples: %s%s\nFull details written to the log file (default: %s)",
            len(duplicates),
            preview,
            "..." if len(duplicates) > const.PREVIEW_LIMIT else "",
            card_loader.normalize_filename(const.FILE_NAME_LOG, const.FILE_TYPE_LOG)
        )
        logger.debug("Duplicate entries: %s", duplicates)