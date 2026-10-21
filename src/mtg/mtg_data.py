"""
Shared MTG data access and interpretation functions.

Provides MTG-level helpers that interpret and resolve data
across shared resources. These functions expose normalized
MTG concepts without depending on format-specific parsing
or workflow orchestration.
"""
from mtg import forge_data
from mtg.forge_edition import ForgeEdition
from mtg.shandalar_types import ShandalarCard
from resources import data_map_loader, lookup_loader
from resources.data_map import DataMap
from resources.forge_card_lookup import ForgeCardLookup
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def map_card(shandalar_id: str, dataset: str | None = None, overwrite_existing: bool = False) -> bool:
    """
    Create or update a Shandalar card-to-Forge edition mapping.

    Resolves the Shandalar card by ID, finds the Forge editions containing
    the card, selects the preferred edition, and adds the resulting reference
    to the Shandalar card-to-Forge edition data map.

    Args:
        shandalar_id: The Shandalar card ID to map.
        dataset: The Shandalar dataset containing the card. If None, the
            default dataset is used.
        overwrite_existing: Whether to replace an existing mapping for
            the specified Shandalar card ID.

    Returns:
        True if a new reference was created or an existing reference was
        overwritten; otherwise False.

    Raises:
        ValueError: If the specified Shandalar card cannot be found in
            the dataset.
    """
    card_map: DataMap | None = data_map_loader.get_shandalar_card_to_forge_edition_map(dataset)
    dataset_name: str = "Default" if dataset is None else dataset

    if card_map is None:
        logger.info(
            "Could not retrieve existing Shandalar card to Forge Edition map for dataset '%s'.\n"
            "Creating a new data map.",
            dataset_name
        )
        card_map = data_map_loader.create_shandalar_card_to_forge_edition_map(
            dataset,
            True
        )

    if shandalar_id in card_map:
        if not overwrite_existing:
            logger.warning(
                "Unable to create new reference for Shandalar card to Forge edition. "
                "Existing entry for card (Shandalar ID: '%s') already exists in "
                "data map at: %s",
                shandalar_id,
                card_map.path
            )
            return False

        logger.info(
            "Existing reference for card (Shandalar ID: '%s') in Shandalar Card "
            "to Forge Edition map for dataset '%s' will be overwritten.",
            shandalar_id,
            dataset_name
        )

    shandalar_lookup: ShandalarCardLookup = lookup_loader.get_shandalar_card_lookup(dataset)
    forge_lookup: ForgeCardLookup = lookup_loader.get_forge_card_lookup()
    shandalar_card: ShandalarCard | None = shandalar_lookup.get(shandalar_id)

    if shandalar_card is None:
        raise ValueError(
            f"Card data could not be found for Shandalar ID '{shandalar_id}' "
            f"in dataset '{dataset_name}'."
        )

    card_name: str = shandalar_card.normalized_name

    candidate_editions: set[ForgeEdition] = forge_lookup.find_card(card_name)

    if not candidate_editions:
        logger.warning(
            "Unable to create new reference for Shandalar card to Forge edition. "
            "Card (Shandalar ID: '%s', normalized name: '%s') cannot be found in Forge data.",
            shandalar_id,
            card_name
        )
        return False

    earliest_edition: ForgeEdition = forge_data.get_earliest_edition(candidate_editions)

    logger.info(
        "Generated new reference for Shandalar card (Shandalar ID: '%s', normalized name: '%s') "
        "to Forge edition '%s'.",
        shandalar_id,
        card_name,
        earliest_edition.name
    )

    card_map[shandalar_id] = earliest_edition.name

    return True

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

def validate_card_reference(shandalar_id: str, dataset: str | None = None) -> bool:
    """
    Validate the Forge edition reference for a Shandalar card.

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

    edition_map: DataMap = data_map_loader.get_active_shandalar_to_forge_edition_map(dataset)
    shandalar_edition: str = shandalar_card.edition
    forge_edition_name: str | None = edition_map.get(shandalar_edition)

    if forge_edition_name is None:
        return False

    forge_edition: ForgeEdition | None = forge_lookup.get(forge_edition_name)

    if forge_edition is None:
        return False

    return shandalar_card.normalized_name in forge_edition.cards