import csv
import func

cards = func.populate_cards([], func.get_editions_list())
unsupported_cards = func.get_unsupported_cards(cards)

unsupported_cards.sort()
print('Writing unsupported cards to output.txt...')
with open('output.txt', 'w', encoding = 'utf-8') as file:
    for element in unsupported_cards:
        file.write(str(element) + '; ')

print('Compilation complete!')