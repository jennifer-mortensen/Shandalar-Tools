"""
Forge-specific domain types.

Defines Forge deck formats and their associated metadata,
along with utilities for parsing and validating supported
Forge format names.
"""
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

# ==============================
# CLASSES
# ==============================
class ForgeCardFields(NamedTuple):
    """
    Parsed fields from a Forge deck entry.

    Attributes:
        quantity: The number of copies.
        name: The card name.
        edition_code: The forge edition code
            used to locate the edition file
            containing the card.
        art_variant: The unique art variant.
    """    
    quantity: int
    name: str
    edition_code: str
    art_variant: int

# ==============================
# PRIVATE CLASSES
# ==============================
@dataclass
class _ForgeFormatData:
    """
    Metadata associated with a Forge deck format.

    Stores the values used to identify and describe a format
    within Forge.
    """
    file_name: str
    format_name: str
    order: str
    subtype: str
    type: str

# ==============================
# ENUMS
# ==============================
class ForgeFormat(Enum):
    """
    Supported Forge deck formats.

    Each format stores the metadata associated with its
    representation in Forge.
    """    
    STANDARD = _ForgeFormatData(file_name="Standard", format_name="Standard", order="101", subtype="Standard", type="Sanctioned")
    PAUPER = _ForgeFormatData(file_name="Pauper", format_name="Pauper", order="108", subtype="Pauper", type="Sanctioned")
    PIONEER = _ForgeFormatData(file_name="Pioneer", format_name="Pioneer", order="102", subtype="Pioneer", type="Sanctioned")
    MODERN = _ForgeFormatData(file_name="Modern", format_name="Modern", order="103", subtype="Modern", type="Sanctioned")
    LEGACY = _ForgeFormatData(file_name="Legacy", format_name="Legacy", order="105", subtype="Legacy", type="Sanctioned")
    VINTAGE = _ForgeFormatData(file_name="Vintage", format_name="Vintage", order="104", subtype="Vintage", type="Sanctioned")
    BRAWL = _ForgeFormatData(file_name="Brawl", format_name="Brawl", order="101", subtype="Commander", type="Casual")
    COMMANDER = _ForgeFormatData(file_name="Commander", format_name="Commander", order="137", subtype="Commander", type="Casual")
    OATHBREAKER = _ForgeFormatData(file_name="Oathbreaker", format_name="Oathbreaker", order="141", subtype="Commander", type="Casual")
    PREDH = _ForgeFormatData(file_name="PreDH", format_name="PreDH", order="", subtype="Commander", type="Casual")
    PREMODERN = _ForgeFormatData(file_name="Premodern", format_name="Premodern", order="106", subtype="", type="Casual")
    HISTORIC = _ForgeFormatData(file_name="Historic", format_name="Historic", order="142", subtype="Arena", type="Digital")
    EXTENDED = _ForgeFormatData(file_name="Extended", format_name="Extended", order="", subtype="Extended", type="Archived")

    @property
    def file_name(self) -> str:
        """Retrieve the Forge format file name."""
        return self.value.file_name

    @property
    def format_name(self) -> str:
        """Retrieve the Forge format name."""
        return self.value.format_name

    @property
    def order(self) -> str:
        """Retrieve the Forge format order."""
        return self.value.order

    @property
    def subtype(self) -> str:
        """Retrieve the Forge format subtype."""
        return self.value.subtype

    @property
    def type(self) -> str:
        """Retrieve the Forge format type."""
        return self.value.type
    
FORGE_FORMAT_VALID_VALUES = [f.name.lower() for f in ForgeFormat]

def parse_forge_format(value: str) -> ForgeFormat:
    """
    Parse a string into a ForgeFormat enum value.

    Performs a case-insensitive lookup against the supported Forge
    format names.

    Args:
        value: The format name to parse.

    Returns:
        The matching ForgeFormat enum value.

    Raises:
        ValueError: If the format name is not recognized.
    """    
    try:
        return ForgeFormat[value.upper()]
    except KeyError:
        raise ValueError(f"Unknown format '{value}'. Valid formats: {FORGE_FORMAT_VALID_VALUES}")