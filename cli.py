import argparse
import card_loader
import card_processor
import const
import os
import sys

# Main entry point.
def main():
    args = parse_args()

    editions = card_loader.get_editions_list(args.editions)
    cards = card_processor.get_card_pool(editions)

    unsupported_cards = card_processor.get_unsupported_cards(cards, card_processor.build_shandalar_lookup())
    user_banned_cards = card_loader.get_user_banned_cards(args.user_banned)
    forge_format = card_processor.generate_forge_format(unsupported_cards, user_banned_cards, card_processor.generate_edition_codes(editions))

    print(f"Writing unsupported cards to {args.output}...")
    with open(args.output, "w", encoding=const.DEFAULT_ENCODING) as file:
        file.write(forge_format)

    print("Compilation complete!")

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