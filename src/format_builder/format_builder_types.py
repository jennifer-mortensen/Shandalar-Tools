"""
Dataclasses and enums for the Shandalar Tools format builder.

Defines the data structures and reference values used throughout the
format builder pipeline, including Forge format metadata, pipeline
input/output models, and format parsing helpers.
"""
from dataclasses import dataclass, field
from mtg.forge_types import ForgeFormat

@dataclass
class ForgeFormatInput:
    """
    User-supplied format specification parsed from a TOML input file.
    """    
    editions: list[str] = field(default_factory=list)
    additional_bans: list[str] = field(default_factory=list)
    additional_cards: list[str] = field(default_factory=list)

@dataclass
class ForgeFormatOutput:
    """Fully resolved format data ready to be rendered and written to disk."""    
    format_type: ForgeFormat
    banned_cards: list[str]
    additional_cards: list[str]
    edition_codes: set[str]

    @property
    def file_name(self) -> str:
        """Retrieve the Forge format file name."""
        return self.format_type.file_name

    @property
    def format_name(self) -> str:
        """Retrieve the Forge format name."""
        return self.format_type.format_name

    @property
    def order(self) -> str:
        """Retrieve the Forge format order."""
        return self.format_type.order

    @property
    def subtype(self) -> str:
        """Retrieve the Forge format subtype."""
        return self.format_type.subtype

    @property
    def type(self) -> str:
        """Retrieve the Forge format type."""
        return self.format_type.type