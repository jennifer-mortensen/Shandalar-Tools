# Shandalar Tools

**Current Version:** 2.0.0.dev0 (Dev Branch)

> ⚠️ **Dev Branch Notice:** This branch is unstable and may change at any time.  
> For a stable release, use the 'main' branch or download from Releases.
> This version is labeled 2.0.0.dev0 to indicate development direction, not progress—it is based on 1.0.3.

A Python command-line utility for generating MTG: Forge format restrictions compatible with Shandalar mods.

MTG: Forge supports cards from many expansions, but Shandalar only implements a subset of them. This tool scans Forge edition files and creates a format definition that bans cards not supported by Shandalar. This allows decks to be built in Forge while ensuring they remain compatible with Shandalar mods.

> **Note:** By default, this tool assumes the 2016 "ProJared" version of Shandalar. To use a different dataset, see **Data Updates** below.

---

## Features

* Loads card lists from MTG: Forge edition files
* Compares them against the Shandalar card pool
* Generates a Forge format file banning unsupported cards
* Supports optional user ban lists for custom restrictions
* Handles duplicate editions gracefully
* Detects file encodings automatically
* Provides detailed logging for diagnostics and debugging

On success, a format file is written and a summary is printed to the console. A log file (`shandalar_tools.log`) is also generated containing detailed diagnostic information, including full duplicate lists and debugging output.

---

## Requirements

### For End Users

* Windows operating system
* No additional dependencies required

### For Developers

* Python 3.9 or newer

---

## Usage

### Windows Executable

```bash
shandalar-tools.exe
```

### Python Source

```bash
python main.py
```

This will:

* Load editions listed in the configuration file
* Compare them against the Shandalar card list
* Generate a Forge format file of unsupported cards (default: `Standard.txt`)

---

## Command-Line Options

| Option                | Description                                               |
| --------------------- | --------------------------------------------------------- |
| `-o`, `--output`      | Specify the output file                                   |
| `-e`, `--editions`    | Specify the CSV file listing editions to load             |
| `-b`, `--user-banned` | Specify the CSV file listing user-designated cards to ban |

### Examples

```bash
shandalar-tools.exe -o unsupported.txt
shandalar-tools.exe -e custom_sets.csv
shandalar-tools.exe -b custom_bans.csv
```

When running from source:

```bash
python main.py -o unsupported.txt
python main.py -e custom_sets.csv
python main.py -b custom_bans.csv
```

---

## Configuration

The editions configuration file (`config.csv`) contains a list of edition names corresponding to Forge edition files.

### Example

```
Ninth Edition
Revised Edition
Ice Age
Homelands
```

Edition files are expected in:

```
data/editions/
```

---

## Distribution Structure

The packaged release includes the following files:

```
shandalar-tools.exe
readme.txt
config.csv
user_banned.csv
data/
├── Shandalar Card List.csv
└── editions/
```

All files must remain in the same directory as the executable.

> **Important:** Shandalar Tools is designed to run from a user-writable directory.  
> Do **not** install it in `Program Files`, as this will prevent the application from writing logs and output files.  
> Recommended locations include the user's **Documents** folder or any portable directory.

---

## Example Output

```
INFO: Loading edition list...
INFO: Building card pool from editions...
INFO: Loading edition 'Ninth Edition'...
INFO: Loading edition 'Revised Edition'...
INFO: Loading edition 'Fourth Edition'...
INFO: Loading edition 'Ice Age'...
INFO: Loading edition 'Homelands'...
INFO: Loading edition 'Alliances'...
INFO: Loading edition 'Time Spiral'...
WARNING: Duplicate edition 'Ninth edition' detected; skipping.
INFO: Loading edition 'Coldsnap'...
INFO: Loading edition 'Fallen Empires'...
INFO: Loading edition 'The Dark'...
INFO: Identifying unsupported cards...
INFO: Identified 557 unsupported cards.
INFO: Loading user-banned card list...
INFO: User-banned file is empty.
INFO: Formatting output for MTG: Forge...
INFO: Generating Scryfall edition codes...
INFO: Collecting edition code for 'Ninth Edition'...
INFO: Collecting edition code for 'Revised Edition'...
INFO: Collecting edition code for 'Fourth Edition'...
INFO: Collecting edition code for 'Ice Age'...
INFO: Collecting edition code for 'Homelands'...
INFO: Collecting edition code for 'Alliances'...
INFO: Collecting edition code for 'Time Spiral'...
INFO: Collecting edition code for 'Ninth edition'...
INFO: Collecting edition code for 'Coldsnap'...
INFO: Collecting edition code for 'Fallen Empires'...
INFO: Collecting edition code for 'The Dark'...
INFO: Writing Forge output to Standard.txt...
INFO: Compilation completed successfully!
```

---

## Project Structure

```
core/
├── card_loader.py       # File parsing and data extraction utilities
├── card_processor.py    # Core processing and transformation logic
└── const.py             # Constants and format templates

main.py                  # Application entry point and CLI interface

data/
├── Shandalar Card List.csv
└── editions/            # MTG: Forge edition files
```

---

## Data Updates

This tool relies on external data files:

* Forge edition files sourced from MTG: Forge (`data/editions/`)
* Shandalar card list sourced from Shandalar (`data/Shandalar Card List.csv`)

### To Update Data

1. Replace the existing data files with updated versions from your MTG: Forge installation or other sources.
2. Ensure filenames and directory structure remain consistent.

No additional configuration is required as long as the file structure is preserved.

---

## Roadmap

### v2 (Deck Translator)

* Deck translation between Shandalar and Forge
* Additional performance improvements if needed

### v2.5 (Refinement & Flexibility)

* Refine existing architecture
* Add header column in `user_banned` to support user-defined sections
* Support additional output formats beyond "Standard"
* Configure Shandalar datasets via parameters

### v3 (Data Updater)

* Sync data from the Forge repository to automatically support new editions

---

## Purpose

This project was created to streamline deck building for Shandalar mods, ensuring that decks created in MTG: Forge contain only cards supported by the game.

It serves as both a practical utility and a demonstration of structured data processing, error handling, and CLI application design developed through iterative refinement.

This tool was developed through real-world use. As new edge cases and data inconsistencies were encountered—such as missing files, encoding issues, and duplicate editions—the design was refined to handle them explicitly and reliably.

The current structure reflects those iterations, prioritizing clear data flow, explicit error handling, and separation between CLI, loading, and processing logic.

In other words: this project was designed for real-world use, not merely to sit in a repository. Expect it to evolve with time.

---

## Design Notes

This project separates data loading, validation, and application control:

* Loader functions return validated data structures. Missing required files raise exceptions, while empty collections represent valid but empty data. This allows the calling layer to determine whether an input is optional or required.
* Empty collections (e.g., `[]`) represent valid but empty data and are handled separately from missing inputs.
* The CLI layer is responsible for validating required inputs and determining whether execution should continue or terminate.
* Helper validation functions may terminate execution early when encountering invalid or missing required data.
* Exceptions are used for malformed or unexpected data, ensuring that invalid states do not silently propagate through the system.

This separation of concerns promotes maintainability, testability, and clarity while aligning with best practices for professional Python application design.

## Version History

### v1.0.3
- Converted inline comments to comprehensive PEP 257–compliant docstrings.
- Refactored Forge format generation for improved clarity and maintainability.
- Added reusable helpers for duplicate detection and sequence merging.
- Improved duplicate detection across unsupported and user-banned lists.
- Introduced abstract type hints (Iterable, Sequence) for greater flexibility and accuracy.
- Ensured deterministic output by sorting edition codes.
- Enhanced logging for clearer diagnostics and debugging.
- Added a module-level docstring to the constants module.

### v1.0.2
- Fixed a crash that can occur when no unsupported cards are found.

### v1.0.1
- Updated documentation for clarity and accuracy.
- Added a user-friendly `readme.txt` for distribution.
- Corrected design notes to reflect current loader behavior.
- Improved consistency between packaged files and documentation.
- No functional changes.

### v1.0
- Initial stable release.
- Generates MTG: Forge format restrictions compatible with Shandalar mods.
- Supports configurable editions and user-defined ban lists.
- Detects duplicate editions and handles file encodings automatically.
- Includes detailed diagnostic logging.
- Distributed as a standalone executable with an installer and portable version.