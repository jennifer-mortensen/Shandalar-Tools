import csv
import func

cards = func.populate_cards([], func.get_editions_list())
unsupported_cards = func.get_unsupported_cards(cards)

unsupported_cards.sort()
with open('output.txt', 'w', encoding = 'utf-8') as file:
    for element in unsupported_cards:
        file.write(str(element) + '; ')

print('Export complete!')