"""
Constants used by Shandalar Tools parsing utilities.

Defines shared parsing constants, including accepted input
values and other constants used by parsing helper functions.
"""
# ==============================
# BOOLEAN LITERALS
# ==============================
TRUE_VALUES = frozenset({"1", "true", "t", "yes", "y", "enable", "on"})
FALSE_VALUES = frozenset({"0", "false", "f", "no", "n", "disable", "off"})