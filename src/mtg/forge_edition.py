"""
Forge edition resource representation.

Defines the ForgeEdition data class, which represents a Forge edition
and its associated card names, release date, edition code, and
Scryfall code.
"""
from common import paths, string_utils
from dataclasses import dataclass, field
from datetime import date
from mtg import forge_data
import logging

logger = logging.getLogger(__name__)

@dataclass
class ForgeEdition:
    """
    Represents a Forge edition and its associated metadata.

    Loads the edition's card names, release date, Forge edition code,
    and Scryfall code when initialized.
    """    
    name: str
    release_date: date | None = field(init=False)
    edition_code: str = field(init=False)
    scryfall_code: str | None = field(init=False)
    _cards: set[str] = field(init=False)

    def is_canonical(self) -> bool:
        """
        Determine whether the edition uses its canonical edition code.

        An edition is canonical when its Forge edition code matches its
        Scryfall code.

        Returns:
            True if the Forge and Scryfall edition codes match,
            otherwise False.
        """        
        return self.edition_code == self.scryfall_code

    def __post_init__(self) -> None:
        """
        Load the edition's data after initialization.
        """        
        self._load()

    def _load(self) -> None:
        """
        Load the edition's cards and metadata from Forge data.
        """        
        logger.debug("Loading Forge edition '%s' from path: %s", self.name, paths.build_edition_file_path(self.name))

        self._cards = string_utils.normalize_set(set(forge_data.get_edition_card_names(self.name)))
        self.release_date = forge_data.get_edition_release_date(self.name)
        self.edition_code = forge_data.get_edition_code(self.name)
        self.scryfall_code = forge_data.get_scryfall_code(self.name)

    def __str__(self) -> str:
        """
        Return the edition name as its string representation.
        """
        return self.name       

    @property
    def cards(self) -> set[str]:
        """
        Return the normalized card names in the edition.

        Returns:
            The normalized card names associated with the edition.
        """
        return self._cards