"""
Shared MTG data access and interpretation functions.

Provides MTG-level helpers that interpret and resolve data
across shared resources. These functions expose normalized
MTG concepts without depending on format-specific parsing
or workflow orchestration.
"""
from mtg.shandalar_types import ShandalarCard
from resources import lookup_loader
from resources.shandalar_card_lookup import ShandalarCardLookup
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
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
