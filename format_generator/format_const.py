"""
Centralized constants for the format generator tool.

This module defines MTG: Forge format templates.
"""

# ==============================
# FORGE FORMAT CONSTRUCTORS
# ==============================

FORGE_FORMAT_BODY_STANDARD = """[format]
Name:Standard
Order:101
Subtype:Standard
Type:Sanctioned
Banned: {banned_cards}
Sets: {set_codes}"""