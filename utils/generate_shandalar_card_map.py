# 1. Shandalar Card ID
# 2. Shandalar Card Data Row
# 3. Edition in Row
# 4. Shandalar Edition Map
# 5. Forge/Scryfall Edition Code
# 6. Expected Forge Edition
# 7. Generate map if not found. Prioritize: Date > Canonical > Alphabetical.

from common import runtime, settings
from resources import data_map_loader, lookup_loader
from resources.data_map import DataMap
from resources.forge_card_lookup import ForgeCardLookup
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

LOG_NAME: str = "shandalar_card_map_generator"

def main() -> None:
    runtime.initialize_runtime(LOG_NAME)

    forge_lookup: ForgeCardLookup = lookup_loader.get_forge_card_lookup()
    shandalar_lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup()
    forge_code_map: DataMap = data_map_loader.get_forge_edition_to_code_map()
    shandalar_edition_map: DataMap = data_map_loader.get_shandalar_to_forge_edition_map(settings.get_shandalar_dataset())
    dataset: str = settings.get_shandalar_dataset()

    broken_references: set[str] = set()

    for card in shandalar_lookup.cards.values():
        edition_name: str = card.get_forge_edition(dataset)
        edition_code: str = forge_code_map[edition_name]

        if edition_name not in forge_lookup:
            logger.warning(f"Missing Forge edition: %s", edition_name)
            continue

        if not forge_lookup.contains_card(card_name=card.name, edition=edition_name):
            broken_references.add(card.name)
            print(
                f"\nBroken Reference #{len(broken_references)}"
                f"\n  Card: {card.name}"
                f"\n  Set: {card.set}"
                f"\n  Forge Code: {edition_code}"
                f"\n  Forge Edition: {edition_name}"
            )

    print(f"\nFound {len(broken_references)} broken references.")

if __name__ == "__main__":
    main()
