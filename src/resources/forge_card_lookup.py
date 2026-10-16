"""
Cached lookup of Forge editions for Shandalar Tools.

Provides a managed resource that loads Forge edition data
and provides edition-level card lookups for card matching
and validation operations.
"""
from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from dataclasses import dataclass, field
from common import path_const, paths, string_utils
from mtg.forge_edition import ForgeEdition
from pathlib import Path
from resources.managed_resource import ManagedResource
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATACLASSES
# ==============================
@dataclass
class ForgeCardLookup(ManagedResource):
    """
    Cached lookup of Forge editions.

    Loads Forge edition files and provides access to their
    card data for card matching and edition-level lookups.
    """
    # Private Members
    _editions: dict[str, ForgeEdition] = field(default_factory=dict)

    # Public Functions
    def contains_card(self, card_name: str, edition: str | None = None) -> bool:
        """
        Determine whether a card exists in the Forge lookup.

        When an edition is specified, searches only that edition.
        Otherwise, searches across all loaded Forge editions.

        Args:
            card_name: The card name to search for.
            edition: Optional Forge edition name to restrict
                the search to.

        Returns:
            True if the card exists in the specified edition,
            or in any loaded Forge edition when no edition is
            provided; otherwise False.
        """
        normalized_card: str = string_utils.normalize_string(card_name)

        if edition is not None:
            forge_edition: ForgeEdition | None = self.get(edition)
            return forge_edition is not None and normalized_card in forge_edition.cards

        return any(normalized_card in forge_edition.cards for forge_edition in self._editions.values())

    # Managed Resource Interface
    def on_terminate(self) -> None:
        """
        No shutdown actions are required.
        """
        pass    

    # Private Functions
    def __post_init__(self) -> None:
        """
        Initialize the lookup after construction.

        Loads Forge card data and populates the lookup cache.
        """        
        self._load()

    def _load(self) -> None:
        """
        Load Forge edition data into the lookup cache.

        Reads all Forge edition files and creates a ForgeEdition
        instance for each edition. Editions containing no cards are
        skipped and logged.
        """
        logger.info("Generating Forge card lookup...")

        editions_dir: Path = paths.get_forge_editions_dir()

        for file in editions_dir.glob(
            f"*{path_const.FILE_EXTENSION_FORGE_EDITION}"
        ):
            edition_name: str = file.stem
            forge_edition: ForgeEdition = ForgeEdition(edition_name)

            if forge_edition.cards:
                self._editions[edition_name] = forge_edition
            else:
                logger.warning("No cards found for edition '%s'.", edition_name)

        logger.info(
            "Generated Forge card lookup with %d entries across %d editions.",
            sum(len(forge_edition.cards) for forge_edition in self._editions.values()),
            len(self._editions)
        )

    # Dictionary Functions
    def __contains__(self, key: str) -> bool:
        """
        Return whether the specified edition exists in the lookup.
        """        
        return key in self._editions

    def __getitem__(self, key: str) -> ForgeEdition:
        """
        Retrieve data for the given edition.

        Args:
            key: Forge edition name.

        Returns:
            The edition as a ForgeEdition.

        Raises:
            KeyError: If the edition does not exist.
        """        
        return self._editions[key]
    
    def __iter__(self) -> Iterator[str]:
        """
        Iterate over Forge edition names.
        """        
        return iter(self._editions)    

    def __len__(self) -> int:
        """
        Return the number of loaded Forge editions.
        """        
        return len(self._editions)
    
    def get(self, key: str, default=None) -> ForgeEdition | None:
        """
        Retrieve data for the given edition.

        Args:
            key: Forge edition name.
            default: Value returned when the edition does not exist.

        Returns:
            The edition data as a ForgeEdition, or default.
        """
        forge_edition: ForgeEdition | None = self._editions.get(key, default)

        if forge_edition is None:
            logger.warning(
                "Attempted to retrieve edition '%s', but no edition was found.",
                key
            )

        return forge_edition

    def items(self) -> ItemsView[str, ForgeEdition]:
        """
        Return a view of edition-to-ForgeEdition mappings.
        """        
        return self._editions.items()

    def keys(self) -> KeysView[str]:
        """
        Return a view of loaded Forge edition names.
        """        
        return self._editions.keys()

    def values(self) -> ValuesView[ForgeEdition]:
        """
        Return a view of loaded Forge editions.
        """        
        return self._editions.values()