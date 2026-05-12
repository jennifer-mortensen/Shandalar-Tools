"""
Constants, dataclasses, and enums for the Shandalar Tools format generator.

Defines the data structures and reference values used throughout the format
pipeline, including Forge format metadata, input/output dataclasses, TOML
key constants, and the Forge format body template.
"""
from dataclasses import dataclass, field
from enum import Enum

# ==============================
# FILE NAMES & TYPES
# ==============================
FILE_TYPE_OUTPUT_FORMAT = "txt"
FILE_TYPE_INPUT_FORMAT = "toml"

# ==============================
# TOML CONSTANTS
# ==============================
INPUT_FORMAT_KEY_EDITIONS = "editions"
INPUT_FORMAT_KEY_ADDITIONAL_BANS = "additional_bans"
INPUT_FORMAT_KEY_ADDITIONAL_CARDS = "additional_cards"

# ==============================
# DATACLASSES & ENUMS
# ==============================
@dataclass
class ForgeFormatData:
    """Static metadata for a Forge format, used to populate the output file."""    
    file_name: str
    name: str
    order: str
    subtype: str
    type: str

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
    format_data: ForgeFormatData
    banned_cards: list[str]
    additional_cards: list[str]
    set_codes: list[str]

class ForgeFormat(Enum):
    STANDARD = ForgeFormatData(file_name="Standard", name="Standard", order="101", subtype="Standard", type="Sanctioned")
    PAUPER = ForgeFormatData(file_name="Pauper", name="Pauper", order="108", subtype="Pauper", type="Sanctioned")
    PIONEER = ForgeFormatData(file_name="Pioneer", name="Pioneer", order="102", subtype="Pioneer", type="Sanctioned")
    MODERN = ForgeFormatData(file_name="Modern", name="Modern", order="103", subtype="Modern", type="Sanctioned")
    LEGACY = ForgeFormatData(file_name="Legacy", name="Legacy", order="105", subtype="Legacy", type="Sanctioned")
    VINTAGE = ForgeFormatData(file_name="Vintage", name="Vintage", order="104", subtype="Vintage", type="Sanctioned")
    BRAWL = ForgeFormatData(file_name="Brawl", name="Brawl", order="101", subtype="Commander", type="Casual")
    COMMANDER = ForgeFormatData(file_name="Commander", name="Commander", order="137", subtype="Commander", type="Casual")
    OATHBREAKER = ForgeFormatData(file_name="Oathbreaker", name="Oathbreaker", order="141", subtype="Commander", type="Casual")
    PREDH = ForgeFormatData(file_name="PreDH", name="PreDH", order="", subtype="Commander", type="Casual")
    PREMODERN = ForgeFormatData(file_name="Premodern", name="Premodern", order="106", subtype="", type="Casual")
    HISTORIC = ForgeFormatData(file_name="Historic", name="Historic", order="142", subtype="Arena", type="Digital")
    EXTENDED = ForgeFormatData(file_name="Extended", name="Extended", order="", subtype="Extended", type="Archived")
    
FORGE_FORMAT_VALID_VALUES = [f.name.lower() for f in ForgeFormat]

def parse_forge_format(value: str) -> ForgeFormat:
    try:
        return ForgeFormat[value.upper()]
    except KeyError:
        raise ValueError(f"Unknown format '{value}'. Valid formats: {FORGE_FORMAT_VALID_VALUES}")

# ==============================
# STRING CONSTRUCTORS
# ==============================
FORGE_FORMAT_BODY = """[format]
Name:{name}
Order:{order}
Subtype:{subtype}
Type:{type}
Banned: {banned_cards}
Additional: {additional_cards}
Sets: {set_codes}"""