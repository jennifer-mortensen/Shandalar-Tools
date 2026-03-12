import argparse
import card_loader
import const
import sys

# Main entry point.
def main():
    args = parse_args()

    editions = card_loader.get_editions_list(args.editions)
    cards = get_card_pool(editions)

    unsupported_cards = get_unsupported_cards(cards)
    forge_format = generate_forge_format(unsupported_cards, True, generate_edition_codes(editions))

    print(f"Writing unsupported cards to {args.output}...")
    with open(args.output, "w", encoding="utf-8") as file:
        file.write(forge_format)

    print("Compilation complete!")

def normalize_editions_filename(filename):
    return f"{filename}.csv" if "." not in filename else filename

def normalize_output_filename(filename):
    return f"{filename}.txt" if "." not in filename else filename

def parse_args():
    parser = argparse.ArgumentParser(
        prog="shandalar-tools", 
        description="Check card compatibility between Shandalar and MTG:Forge.",
        epilog="Examples:\n  %(prog)s\n  %(prog)s -e custom_sets.csv\n  %(prog)s -o unsupported.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument(
        "-o", "--output",
        type=normalize_output_filename,
        default="output.txt",
        help="File to write unsupported cards to."
    )
    parser.add_argument(
        "-e", "--editions",
        type=normalize_editions_filename,
        default=const.file_config,
        help="CSV file listing editions to load."                  
    )
    return parser.parse_args()

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def get_unsupported_cards(cards):
    print("Checking unsupported cards...")
    unsupported_cards = []
    shandalar_cards = card_loader.sanitize_set(card_loader.get_shandalar_cards())
    
    for c in cards:
        if card_loader.sanitize_name(c) not in shandalar_cards:
            unsupported_cards.append(c)
    print(f"Found {len(unsupported_cards)} unsupported cards.")
    return unsupported_cards

# Returns a set containing all cards from the given editions.           
def get_card_pool(editions):
    editions_loaded = set()
    cards = set()

    print("Compiling source card list...")
    for e in editions:
        print(f"Loading {e} ...")
        if card_loader.sanitize_name(e) in editions_loaded:
            print(f"Duplicate detected. Skipping {e}.")
        else:    
            edition_cards = card_loader.get_edition_cards(e)
            if edition_cards is None:
                print(f"Error: Could not load file at {card_loader.get_edition_file_path(e)}.")
                print("Terminating.")
                sys.exit(1)
            else:
                cards.update(edition_cards)
                editions_loaded.add(card_loader.sanitize_name(e))        
    return cards

# Formats output for the MTG Forge format.
def generate_forge_format(cards, sort_cards, edition_codes):
    print("Formatting cards to MTG Forge format...")
    
    formatted_cards = cards.copy()
    if sort_cards:
        formatted_cards.sort()

    banned_cards = "; ".join(formatted_cards)
    set_codes = ", ".join(edition_codes)

    forge_format = const.forge_format_body_standard.format(
        banned_cards = banned_cards,
        set_codes = set_codes
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
            print(f"Could not resolve set code for {e}.")
            print("Terminating.")
            sys.exit(1)
        edition_codes.add(code)

    return edition_codes

if __name__ == "__main__":
    main()