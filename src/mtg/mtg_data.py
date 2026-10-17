"""
Shared MTG data access and interpretation functions.

Provides MTG-level helpers that interpret and resolve data
across shared resources. These functions expose normalized
MTG concepts without depending on format-specific parsing
or workflow orchestration.
"""
from common import paths
from mtg.forge_edition import ForgeEdition
from mtg.shandalar_types import ShandalarCard
from resources import data_map_const, data_map_loader, lookup_loader
from resources.data_map import DataMap
from resources.forge_card_lookup import ForgeCardLookup
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def map_card(shandalar_id: str, dataset: str | None = None, overwrite_existing: bool = False) -> None:
    card_map: DataMap
    
    try:
        card_map = data_map_loader.get_shandalar_card_to_forge_edition_map(dataset)
    except FileNotFoundError:
        logger.info("Could not retrieve existing Shandalar card to Forge Edition map for dataset '%s'.\nCreating a new data map.", "Default" if dataset is None else dataset)
        card_map = DataMap(
            display_name=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_DISPLAY_NAME,
            map_key=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_KEY,
            version=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_VERSION
        )
        card_map.persist_to(paths.build_shandalar_card_to_forge_edition_map_file_path(dataset))

def shandalar_id_to_forge_edition_code(shandalar_id: str, dataset: str | None = None) -> str:
    """
    Resolve a Shandalar card ID to its corresponding Forge edition code.

    Retrieves the specified Shandalar card from the requested dataset
    and resolves its Forge edition code using the configured edition
    mapping.

    Args:
        shandalar_id: The Shandalar card ID to resolve.
        dataset: Optional dataset used for card and edition lookup.

    Returns:
        The corresponding Forge edition code.

    Raises:
        ValueError: If the specified Shandalar card ID is unknown.
    """    
    lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)

    card: ShandalarCard = lookup.get(shandalar_id)
    if card is None:
        raise ValueError(f"Unknown Shandalar card ID: '{shandalar_id}'")

    return card.get_forge_code(dataset)

def validate_card_link(shandalar_id: str, dataset: str | None = None) -> bool:
    """
    Validate the Forge edition linked to a Shandalar card.

    Resolves the Shandalar card and its mapped Forge edition, then
    determines whether the card exists in the mapped Forge edition.

    Args:
        shandalar_id: The Shandalar card ID to validate.
        dataset: The Shandalar dataset containing the card. If None,
            the default dataset is used.

    Returns:
        True if the mapped Forge edition contains the Shandalar card;
        otherwise False.
    """    
    forge_lookup: ForgeCardLookup = lookup_loader.get_forge_card_lookup()
    shandalar_lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)
    shandalar_card: ShandalarCard | None = shandalar_lookup.get(shandalar_id)

    if shandalar_card is None:
        return False

    edition_map: DataMap = data_map_loader.get_shandalar_to_forge_edition_map(dataset)
    shandalar_edition: str = shandalar_card.edition
    forge_edition_name: str | None = edition_map.get(shandalar_edition)

    if forge_edition_name is None:
        return False

    forge_edition: ForgeEdition | None = forge_lookup.get(forge_edition_name)

    if forge_edition is None:
        return False

    return shandalar_card.name in forge_edition.cards