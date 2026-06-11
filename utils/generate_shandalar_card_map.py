# 1. Shandalar Card ID
# 2. Shandalar Card Data Row
# 3. Edition in Row
# 4. Shandalar Edition Map
# 5. Forge/Scryfall Edition Code
# 6. Expected Forge Edition
# 7. Generate map if not found. Prioritize: Date > Canonical > Alphabetical.

from common import common_utils, runtime
from mtg import forge_data, shandalar_data
from mtg.shandalar_types import ShandalarCard

LOG_NAME: str = "shandalar_card_map_generator"

def main() -> None:
    runtime.initialize_runtime(LOG_NAME)

    forge_lookup: dict[str, set[str]] = forge_data.build_forge_card_name_lookup()
    forge_scryfall_map: dict[str, str] = forge_data.read_forge_scryfall_map()
    shandalar_lookup: dict[str, ShandalarCard] = shandalar_data.build_shandalar_card_id_lookup()
    edition_map: dict[str, str] = shandalar_data.read_shandalar_edition_map()

    broken_references: set[str] = set()

    for card in shandalar_lookup.values():
        scryfall_code: str = card.resolve_set(edition_map)

        if scryfall_code not in forge_scryfall_map:
            print(f"Missing Scryfall code: {scryfall_code}")
            continue

        edition_name: str = forge_scryfall_map[scryfall_code]

        if edition_name not in forge_lookup:
            print(f"Missing Forge edition: {edition_name}")
            continue

        if not forge_data.card_exists(
            edition_name=edition_name,
            card_name=card.name,
            forge_card_name_lookup=forge_lookup
        ):
            broken_references.add(card.name)

            print(
                f"\nBroken Reference #{len(broken_references)}"
                f"\n  Card: {card.name}"
                f"\n  Set: {card.set}"
                f"\n  Scryfall: {scryfall_code}"
                f"\n  Forge Edition: {edition_name}"
            )

    print(f"\nFound {len(broken_references)} broken references.")

if __name__ == "__main__":
    main()
