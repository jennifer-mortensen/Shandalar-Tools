import csv
import card_loader
import sys

# Main entry point.
def main():
    cards = get_card_pool(card_loader.get_editions_list())
    unsupported_cards = get_unsupported_cards(cards)

    unsupported_cards.sort()
    print('Writing unsupported cards to output.txt...')
    with open('output.txt', 'w', encoding = 'utf-8') as file:
        file.write('; '.join(unsupported_cards))

print('Compilation complete!')

# Returns a list containing all cards that do not exist in Shandalar from the given set.
def get_unsupported_cards(cards):
    print('Checking incompatible cards...')
    unsupported_cards = []
    shandalar_cards = card_loader.sanitize_set(card_loader.get_shandalar_cards())
    
    for c in cards:
        if card_loader.sanitize_name(c) not in shandalar_cards:
            unsupported_cards.append(c)
    print('Found ' + str(len(unsupported_cards)) + ' incompatible cards.')
    return unsupported_cards

# Returns a set containing all cards from the given editions.           
def get_card_pool(editions):
    editions_loaded = set()
    cards = set()

    print('Compiling source card list...')
    for e in editions:
        print('Loading ' + e + '...')
        if card_loader.sanitize_name(e) in editions_loaded:
            print('Duplicate detected. Skipping ' + e + '.')
        else:    
            edition_cards = card_loader.get_edition_cards(e)
            if edition_cards is None:
                print('Could not load file at ' + card_loader.get_edition_file_path(e) + '.')
                print('Terminating application.')
                sys.exit(1)
            else:
                cards.update(edition_cards)
                editions_loaded.add(card_loader.sanitize_name(e))        
    return cards

if __name__ == "__main__":
    main()