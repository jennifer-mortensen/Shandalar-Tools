# Shandalar Tools

**Current Version:** 2.0.0.dev0 (Dev Branch)

> ⚠️ **Dev Branch Notice:** This branch is unstable and may change at any time.
> For a stable release, use the `main` branch or download from Releases.
> This version is labeled `2.0.0.dev0` to indicate development direction, not progress—it is based on `1.0.3`.

A Python command-line toolkit for generating MTG: Forge format files compatible with Shandalar mods.

MTG: Forge supports cards from many expansions, while Shandalar implementations typically support only a subset of those cards. Shandalar Tools processes Forge edition data and user-defined format specifications to generate Forge-compatible format files that automatically ban unsupported cards while supporting optional custom bans and explicit card additions.

Format definitions are driven by TOML configuration files, allowing formats to be customized, validated, and reproduced consistently across environments.

> **Note:** By default, this tool uses the 2016 “ProJared” Shandalar card pool. Alternate datasets can be configured through the configuration system.

---

## Features

* Generates MTG: Forge format files compatible with Shandalar-compatible card pool datasets
* Uses TOML-based format definitions for reproducible and customizable builds
* Supports configurable Forge output formats (Standard, Modern, Commander, Extended, etc.)
* Automatically detects and bans cards unsupported by the selected Shandalar dataset
* Supports additional user-defined bans and explicit card additions
* Detects conflicts, redundant bans, redundant additions, and duplicate editions
* Automatically detects file encodings with configurable scan modes
* Provides structured logging for diagnostics, validation, and debugging
* Separates configuration, parsing, processing, validation, and pipeline orchestration into modular components

On success, a Forge-compatible format file is written to the configured output directory and a summary is printed to the console. A log file (`shandalar_tools.log`) is also generated containing detailed diagnostics, duplicate reports, warnings, and debugging output.

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
format-generator.exe
```

### Python Source

```bash
python cli/run_format_generator.py
```

This will:

* Load a user-defined TOML format specification
* Build a card pool from the selected Forge editions
* Compare that card pool against the configured Shandalar dataset
* Resolve unsupported cards, custom bans, and explicit additions
* Generate a Forge-compatible format file

---

## Command-Line Options

| Option                  | Description                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------- |
| `-o`, `--output-format` | Specify the Forge format type to generate (`standard`, `modern`, `commander`, etc.) |
| `-i`, `--input-file`    | Specify the TOML format definition file to load                                     |
| `-s`, `--encoding-scan` | Encoding detection mode: `auto`, `fast`, or `full`                                  |
| `-e`, `--editions`      | Deprecated compatibility flag. No longer used.                                      |
| `-b`, `--user-banned`   | Deprecated compatibility flag. No longer used.                                      |

> **Note:** `--encoding-scan auto` is the recommended setting and is designed to work reliably with the bundled data files.
> `--encoding-scan full` is included primarily for compatibility with future or externally sourced data sets that may require complete file scanning.
> `--encoding-scan fast` is provided for completeness, but may fail to detect some encoding issues.

### Examples

```bash
format-generator.exe
format-generator.exe -o modern
format-generator.exe -i custom_format.toml
format-generator.exe -s full
```

When running from source:

```bash
python cli/run_format_generator.py
python cli/run_format_generator.py -o modern
python cli/run_format_generator.py -i custom_format.toml
python cli/run_format_generator.py -s full
```

---

## Configuration

Shandalar Tools uses TOML-based configuration and format definition files.

### Global Configuration

Global application settings are stored in:

```text
user/config/config.toml
```

This file controls shared settings such as:

* Selected Shandalar dataset
* Encoding scan behavior
* Logging behavior
* Default format generation settings

### Input Format Definitions

User-defined format specifications are stored in:

```text
user/formats/
```

Each format definition is a TOML file describing:

* Forge editions to include
* Additional banned cards
* Explicitly allowed cards

### Example

```toml
editions = [
    "Ninth Edition",
    "Ice Age",
    "Homelands"
]

additional_bans = [
    "Black Lotus"
]

additional_cards = [
    "Mana Drain"
]
```

Forge edition files are expected in:

```text
data/editions/
```

---

## Portable Release Structure

The packaged portable release includes the following structure:

```text
Shandalar-Tools/
├── format-generator.exe
├── readme.txt
├── data/
│   ├── editions/
│   └── shandalar_2016.csv
├── logs/
└── user/
    ├── config/
    │   └── config.toml
    ├── formats/
    ├── output_deck_translator/
    └── output_format_generator/
```

All directories should remain relative to the executable.

> **Important:** Shandalar Tools is designed to run from a user-writable directory.
> Do **not** install it in `Program Files`, as this may prevent the application from writing logs, configuration files, and generated output.
> Recommended locations include the user's **Documents** folder or any portable directory.

---

## Example Output

```text
INFO: Reading configuration file...
INFO: Opening custom format file...
INFO: Parsing editions list from custom format...
INFO: Parsing additional bans from custom format...
INFO: Parsing additional cards from custom format...
INFO: Preparing output format for MTG: Forge...
INFO: Checking for conflicts between additional bans and additional cards...
INFO: No conflicts found!
INFO: Loading Shandalar card pool...
INFO: Building card pool from editions...
WARNING: Duplicate edition 'Ninth Edition' detected; skipping.
INFO: Resolving cards from custom format that are not supported in Shandalar...
INFO: Identified 557 unsupported cards.
INFO: Checking for custom additions that are not supported in Shandalar...
INFO: No unsupported additions found!
INFO: Checking for redundant custom additions...
INFO: No redundant additions found!
INFO: Checking for redundant bans...
WARNING: 5 duplicate entries detected across the unsupported and additional bans lists.
INFO: Finalizing ban list...
INFO: Finalizing output format for MTG: Forge...
INFO: Generating Scryfall edition codes...
INFO: Writing MTG: Forge format...
INFO: Compilation completed successfully!
```

---

## Project Structure

```text
Shandalar-Tools/
├── cli/
│   ├── run_deck_translator.py
│   └── run_format_generator.py
├── data/
│   ├── editions/
│   └── shandalar_2016.csv
├── logs/
├── src/
│   ├── common/
│   │   ├── common_const.py
│   │   ├── common_utils.py
│   │   ├── file_utils.py
│   │   ├── log_utils.py
│   │   └── toml_utils.py
│   ├── config/
│   │   ├── common_config.py
│   │   ├── config_io.py
│   │   ├── deck_translator_config.py
│   │   └── format_generator_config.py
│   ├── deck_translator/
│   │   └── translator_const.py
│   └── format_generator/
│       ├── card_loader.py
│       ├── card_processor.py
│       ├── format_const.py
│       └── format_pipeline.py
└── user/
    ├── config/
    │   └── config.toml
    ├── formats/
    ├── output_deck_translator/
    └── output_format_generator/
```

---

## Data Updates

Shandalar Tools relies on two external data sources:

* Forge edition files stored in `data/editions/`
* Shandalar-compatible card pool datasets stored in `data/`

By default, the project includes the `shandalar_2016.csv` dataset.

### Adding Additional Shandalar Data Sets

Additional Shandalar datasets can be added manually by placing compatible CSV files in the `data/` directory.

Once added, the active dataset can be selected through:

```toml
[data]
shandalar_card_pool = "shandalar_2016"
```

The configured value may be specified with or without the `.csv` extension.

### Updating Forge Edition Files

To update Forge edition data:

1. Replace or add edition files in `data/editions/`
2. Preserve the expected Forge edition file structure and naming conventions

No additional configuration is required as long as the directory structure remains consistent.

---

## Roadmap

### v2 (Deck Translator)

* Implement deck translation support between Shandalar and MTG: Forge

### v3 (Data Updater)

* Add tooling for automated synchronization and updating of Forge edition data

---

## Purpose

This project was created to streamline deck building for Shandalar mods by generating MTG: Forge format files that accurately reflect the card support limitations of configurable Shandalar data sets.

It also serves as a practical example of structured CLI application design, modular data processing, configuration-driven workflows, and defensive handling of inconsistent real-world data.

The architecture evolved through iterative real-world use. As new edge cases and data inconsistencies were encountered—such as duplicate editions, malformed rows, missing metadata, and encoding issues—the tooling was refined to detect, validate, and handle them explicitly rather than silently failing or producing ambiguous output.

The current structure emphasizes clear data flow and separation of concerns between configuration loading, file parsing, validation, processing logic, and pipeline orchestration in order to improve maintainability, extensibility, and long-term reliability.

This project was designed as a practical tool intended for continued real-world use and iteration, not merely as a static repository example.

---

## Design Notes

This project separates configuration, loading, validation, processing, and CLI orchestration into distinct layers:

* Loader functions return validated data structures while allowing the calling layer to determine whether missing or empty data is acceptable for a given workflow.
* Empty collections (such as `[]`) are treated as valid inputs and handled separately from missing or malformed data.
* Configuration loading is centralized through typed dataclass-based configuration objects and TOML parsing helpers.
* The CLI layer is responsible for argument validation, top-level execution flow, and determining whether execution should continue or terminate.
* Validation and pipeline helpers explicitly detect conflicts, duplicate entries, unsupported additions, and redundant operations before output generation.
* Exceptions are used for malformed or unexpected states to prevent invalid data from silently propagating through the system.
* Logging is separated into user-facing console output and detailed file-based diagnostics to improve both usability and debuggability.

This separation of concerns promotes maintainability, testability, clarity, and incremental extensibility while aligning with established Python application design practices.

---

## Version History

### v2.0.0.dev0

* Reworked the application around a TOML-driven configuration and format pipeline architecture.
* Replaced CSV-based edition and ban configuration with structured TOML format definitions.
* Added support for configurable Forge output formats (Standard, Modern, Commander, Extended, etc.).
* Introduced explicit pipeline stages for parsing, validation, resolution, output construction, and rendering.
* Added support for additional card inclusions alongside custom bans.
* Added validation for conflicting, redundant, and unsupported user-defined entries.
* Refactored configuration handling into typed dataclass-based config modules.
* Split shared functionality into dedicated utility modules for logging, file handling, TOML parsing, and common helpers.
* Added configurable Shandalar dataset selection through `config.toml`.
* Added configurable encoding scan modes (`auto`, `fast`, `full`).
* Reorganized the repository structure into modular `src/`, `user/`, and CLI layers.
* Improved separation of concerns between CLI orchestration, data loading, validation, processing, and output generation.
* Expanded Forge format generation from a hardcoded Standard template into generalized format metadata and rendering models.
* Improved diagnostics, validation logging, and runtime error reporting throughout the pipeline.
* Added initial Deck Translator project structure and configuration scaffolding.

### v1.0.3

* Converted inline comments to comprehensive PEP 257–compliant docstrings.
* Refactored Forge format generation for improved clarity and maintainability.
* Added reusable helpers for duplicate detection and sequence merging.
* Improved duplicate detection across unsupported and user-banned lists.
* Introduced broader abstract type hints (`Iterable`, `Sequence`) for increased flexibility. *(Later removed during the v2 architecture refactor in favor of simpler concrete interfaces.)*
* Ensured deterministic output by sorting edition codes.
* Enhanced logging for clearer diagnostics and debugging.
* Added a module-level docstring to the constants module.

### v1.0.2

* Fixed a crash that can occur when no unsupported cards are found.

### v1.0.1

* Updated documentation for clarity and accuracy.
* Added a user-friendly `readme.txt` for distribution.
* Corrected design notes to reflect current loader behavior.
* Improved consistency between packaged files and documentation.
* No functional changes.

### v1.0

* Initial stable release.
* Generates MTG: Forge format restrictions compatible with Shandalar mods.
* Supports configurable editions and user-defined ban lists.
* Detects duplicate editions and handles file encodings automatically.
* Includes detailed diagnostic logging.
* Distributed as a standalone executable with an installer and portable version.