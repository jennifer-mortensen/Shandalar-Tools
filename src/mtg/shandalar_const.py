"""
Shandalar-specific constants and parsing metadata.

Defines dataset field indexes, deck structure rules, sideboard
constraints, identifier formats, and other constants used when
reading and writing Shandalar data and deck files.
"""
from mtg.mtg_types import Color

# ==============================
# DATASET FIELDS
# ==============================
SHANDALAR_DATA_FIELD_CARD_NAME: int = 0
SHANDALAR_DATA_FIELD_RELEASE_DATE: int = 1
SHANDALAR_DATA_FIELD_SET: int = 2
SHANDALAR_DATA_FIELD_RARITY: int = 3
SHANDALAR_DATA_FIELD_SHANDALAR_ID: int = 4
SHANDALAR_DATA_FIELD_GATHERER_ID: int = 5
SHANDALAR_DATA_FIELD_TYPE: int = 6
SHANDALAR_DATA_FIELD_COST: int = 7
SHANDALAR_DATA_FIELD_POWER: int = 8
SHANDALAR_DATA_FIELD_TOUGHNESS: int = 9
SHANDALAR_DATA_FIELD_TEXT: int = 10
SHANDALAR_DATA_FIELD_CTYPE: int = 11
SHANDALAR_DATA_FIELD_COLOR_IDENTITY: int = 12

# ==============================
# SIDEBOARD RULES
# ==============================
SHANDALAR_SIDEBOARD_HEADER: dict[str, Color] = {
    # Color order matches typical Shandalar deck pattern rather than proper MTG ordering,
    # though it makes no difference in practice.
    # Case insensitive.
    ".vnone": Color.NONE,
    ".vblack": Color.BLACK,
    ".vblue": Color.BLUE,
    ".vgreen": Color.GREEN,
    ".vred": Color.RED,
    ".vwhite": Color.WHITE
}

# ==============================
# DECK STRUCTURE
# ==============================
# Title
SHANDALAR_DECK_TITLE_LINE: int = 1
SHANDALAR_DECK_TITLE_DELIMITER: str = "("

# Cards
SHANDALAR_CARD_FIELD_ID: int = 0
SHANDALAR_CARD_FIELD_QUANTITY: int = 1
SHANDALAR_CARD_FIELD_NAME: int = 2
SHANDALAR_CARD_MINIMUM_FIELDS: int = 2

# ==============================
# IDENTIFIERS
# ==============================
SHANDALAR_ID_PREFIX: str = "."

# ==============================
# FORMAT STRINGS
# ==============================
# Shandalar Deck Output
SHANDALAR_DECK_BODY: str = """{name} {color_identity}

{card_list}

.vNone
{sideboard_vNone}
.vBlack
{sideboard_vBlack}
.vBlue
{sideboard_vBlue}
.vGreen
{sideboard_vGreen}
.vRed
{sideboard_vRed}
.vWhite
{sideboard_vWhite}
"""

# Forge Card Entry
SHANDALAR_CARD_ENTRY = "{shandalar_id}\t{quantity}\t{name}"