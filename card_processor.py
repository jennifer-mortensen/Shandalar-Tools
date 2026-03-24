import card_loader
import const
import sys

# ==============================
# DATA CONSTRUCTION
# ==============================

# Returns a set containing all cards from the given editions.           
def get_card_pool(editions):
    editions_loaded = set()
    cards = set()

    print("Compiling source card list...")
    for e in editions:
        print(f"Loading {e}...")
        sanitized_edition_name = card_loader.sanitize_name(e)
        if sanitized_edition_name in editions_loaded:
            print(f"Duplicate detected. Skipping {e}.")
            continue

        edition_cards = card_loader.get_edition_cards(e)
        if edition_cards is None:
            sys.exit(f"Error: Could not load file at {card_loader.get_edition_file_path(e)}.")

        cards.update(edition_cards)
        editions_loaded.add(sanitized_edition_name)

    return cards

# Returns a set of edition codes for the given editions list.
def generate_edition_codes(editions):
    # To do: filter out duplicates earlier in the pipeline
    print("Generating edition codes...")
    edition_codes = set()

    for e in editions:
        code = card_loader.get_edition_code(e)
        if code is None:
            sys.exit(f"Could not resolve set code for {e}.")
        edition_codes.add(code)

    return edition_codes

# ==============================
# DATA TRANSFORMATION
# ==============================

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def get_unsupported_cards(cards, shandalar_lookup):
    print("Checking unsupported cards...")

    unsupported_cards = [c for c in cards if card_loader.sanitize_name(c) not in shandalar_lookup]
    print(f"Found {len(unsupported_cards)} unsupported cards.")
    
    return unsupported_cards

# ==============================
# OUTPUT FORMATTING
# ==============================

# Formats output for the MTG Forge format.
def generate_forge_format(cards, user_banned_cards, edition_codes, sort_cards=True):
    print("Formatting cards to MTG Forge format...")

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

            print(
                f"Warning: {len(duplicates)} duplicate entries detected "
                f"in user-banned list (preserved as-is). "
                f"Examples: {preview}"
                + ("..." if len(duplicates) > {const.PREVIEW_LIMIT} else "")
            )

    banned_cards = "; ".join(formatted_cards)
    set_codes = ", ".join(edition_codes)

    forge_format = const.FORGE_FORMAT_BODY_STANDARD.format(
        banned_cards=banned_cards,
        set_codes=set_codes
    )

    return forge_format

# ==============================
# HELPERS
# ==============================

# Returns a sanitized set of shandalar cards for comparison.
def build_shandalar_lookup():
    return card_loader.sanitize_set(card_loader.get_shandalar_cards())