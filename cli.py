import argparse
import card_loader
import const
import os
import sys

# Main entry point.
def main():
    args = parse_args()

    editions = card_loader.get_editions_list(args.editions)
    cards = get_card_pool(editions)

    unsupported_cards = get_unsupported_cards(cards)
    user_banned_cards = get_user_banned_cards(args.user_banned)
    forge_format = generate_forge_format(unsupported_cards, user_banned_cards, generate_edition_codes(editions))

    print(f"Writing unsupported cards to {args.output}...")
    with open(args.output, "w", encoding="utf-8") as file:
        file.write(forge_format)

    print("Compilation complete!")

def normalize_filename(filename, extension):
    return filename if os.path.splitext(filename)[1] else f"{filename}.{extension}"

def parse_args():
    parser = argparse.ArgumentParser(
        prog="shandalar-tools", 
        description="Check card compatibility between Shandalar and MTG:Forge.",
        epilog="Examples:\n  %(prog)s\n  %(prog)s -e custom_sets.csv\n  %(prog)s -o unsupported.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument(
        "-o", "--output",
        type=lambda filename: normalize_filename(filename, "txt"),
        default="output.txt",
        help="File to write unsupported cards to."
    )
    parser.add_argument(
        "-e", "--editions",
        type=lambda filename: normalize_filename(filename, "csv"),
        default=const.file_config,
        help="CSV file listing editions to load."                  
    )
    parser.add_argument(
        "-b", "--user-banned",
        type=lambda filename: normalize_filename(filename, "csv"),
        default=const.file_user_banned,
        help="CSV file listing user-designated cards to ban."                  
    )    
    return parser.parse_args()

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def get_unsupported_cards(cards):
    print("Checking unsupported cards...")

    shandalar_cards = card_loader.sanitize_set(card_loader.get_shandalar_cards())
    unsupported_cards = [c for c in cards if card_loader.sanitize_name(c) not in shandalar_cards]
    print(f"Found {len(unsupported_cards)} unsupported cards.")
    
    return unsupported_cards

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
                + ("..." if len(duplicates) > 5 else "")
            )

    banned_cards = "; ".join(formatted_cards)
    set_codes = ", ".join(edition_codes)

    forge_format = const.forge_format_body_standard.format(
        banned_cards=banned_cards,
        set_codes=set_codes
    )

    return forge_format

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

# Returns a list of user-banned cards.
def get_user_banned_cards(filename):
    print("Loading user-banned cards...")

    user_banned_cards = card_loader.get_csv_column(filename, 0, ",", 0, "", ["#"])
    if user_banned_cards is None:
        print("Could not find user-banned cards.")
        return []

    return user_banned_cards

if __name__ == "__main__":
    main()