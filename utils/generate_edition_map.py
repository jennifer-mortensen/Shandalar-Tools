from common import common_const, path_utils, runtime
from mtg import forge_data
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def main() -> None:
    runtime.initialize_runtime("edition_mapper")
    
    edition_map: dict[str, str] = {}
    
    for file in common_const.EDITIONS_DIR.glob(f"*{common_const.FILE_TYPE_FORGE_EDITION}"):
        edition_name: str = file.stem
        scryfall_code: str = forge_data.get_scryfall_code(edition_name)

        if scryfall_code in edition_map:
            logger.warning(
                "Could not map scryfall code '%s' to edition '%s' because code was already assigned to '%s'.",
                scryfall_code,
                edition_name,
                edition_map[scryfall_code]
            )
            continue

        edition_map[scryfall_code] = edition_name

if __name__ == "__main__":
    main()