"""
File-related constants for Shandalar Tools.

Defines shared constants used for file reading, encoding
detection, and text parsing operations.
"""
# ==============================
# FILE ENCODING
# ==============================
DEFAULT_ENCODING: str = "utf-8"
FALLBACK_ENCODING: str = "latin-1"
FILE_ENCODINGS: list[str] = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
FILE_ENCODING_READ_SIZE_DEFAULT: int = 10240

# ==============================
# CSV / TEXT PARSING
# ==============================
DEFAULT_CSV_DELIMITER: str = ","
COMMENT_PREFIX: str = "#"