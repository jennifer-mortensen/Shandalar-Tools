import argparse
import card_loader
import card_processor
import const
import sys

# Main entry point.
def main():
    args = parse_args()

    print("Checking editions to load...")
    editions = card_loader.get_editions_list(args.editions)
    if editions is None:
        fail(f"Could not find editions file: {args.editions}")
    elif len(editions) == 0:
        fail(f"Editions file is empty: {args.editions}")

    print("Compiling source card list...")
    try:
        cards = card_processor.get_card_pool(editions)
    except FileNotFoundError as e:
        fail(e)
    if not cards:
        fail("No cards were loaded from the provided editions. All edition files may be empty or invalid.")

    print("Checking unsupported cards...")
    unsupported_cards = card_processor.get_unsupported_cards(cards, card_processor.build_shandalar_lookup())
    if not unsupported_cards:
        print(f"Warning: No unsupported cards found among {len(cards)} cards. This is highly unusual and may indicate an issue with the input data or configuration.")
    
    print("Loading user-banned cards...")
    user_banned_cards = card_loader.get_user_banned_cards(args.user_banned)
    if user_banned_cards is None:
        print("Could not find user-banned cards.")
    elif len(user_banned_cards) == 0:
        print("User-banned cards was found, but list was empty.")

    print("Formatting cards to MTG Forge format...")
    try:
        forge_format = card_processor.generate_forge_format(unsupported_cards, user_banned_cards, card_processor.generate_edition_codes(editions))
    except ValueError as e:
        fail(e)        

    print(f"Writing unsupported cards to {args.output}...")
    try:
        with open(args.output, "w", encoding=const.DEFAULT_ENCODING) as file:
            file.write(forge_format)
    except OSError as e:
        fail(f"Could not write to output file: {e}")

    print("Compilation complete!")

def fail(message):
    print(f"Error: {message}")
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="shandalar-tools", 
        description="Check card compatibility between Shandalar and MTG:Forge.",
        epilog="Examples:\n  %(prog)s\n  %(prog)s -e custom_sets.csv\n  %(prog)s -o unsupported.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument(
        "-o", "--output",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_OUTPUT),
        default=const.FILE_NAME_OUTPUT,
        help="File to write unsupported cards to."
    )
    parser.add_argument(
        "-e", "--editions",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_CONFIG),
        default=const.FILE_NAME_CONFIG,
        help="CSV file listing editions to load."                  
    )
    parser.add_argument(
        "-b", "--user-banned",
        type=lambda filename: card_loader.normalize_filename(filename, const.FILE_TYPE_USER_BANNED),
        default=const.FILE_NAME_USER_BANNED,
        help="CSV file listing user-designated cards to ban."                  
    )    
    return parser.parse_args()

if __name__ == "__main__":
    main()