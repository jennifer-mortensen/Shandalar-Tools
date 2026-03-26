SHANDALAR TOOLS
===============

A Python command-line utility for generating MTG: Forge format restrictions
compatible with Shandalar mods.

MTG: Forge supports cards from many expansions, but Shandalar only
implements a subset of them. This tool scans Forge edition files and creates a
format definition that bans cards not supported by Shandalar.

This allows decks to be built in Forge while ensuring they remain compatible
with Shandalar mods.

NOTE: By default, this tool assumes the 2016 "ProJared" version of Shandalar.
To use a different data source, see "DATA UPDATES" below.

FEATURES
========

* Loads card lists from MTG: Forge edition files
* Compares them against the Shandalar card pool
* Generates a Forge format file banning unsupported cards
* Supports optional user ban lists for custom restrictions
* Handles duplicate editions gracefully
* Detects file encodings automatically

On success, a format file will be written and a summary printed to the console.
A log file (default: shandalar_tools.log) is also generated containing detailed 
diagnostic information, including full duplicate lists and debugging output.

REQUIREMENTS
============

* Python 3.9+

USAGE
=====

Basic usage:

python main.py

This will:

* Load editions listed in the configuration file
* Compare them against the Shandalar card list
* Generate a Forge format file of unsupported cards (default: Standard.txt)

OPTIONS
=======

-o, --output
Specify the output file.

Example:
python main.py -o unsupported.txt

-e, --editions
Specify the CSV file listing editions to load.

-b, --user-banned
Specify the CSV file listing user-designated cards to ban.

Example:
python main.py -e custom_sets.csv

CONFIGURATION
=============

The editions configuration file (default: config.csv) contains a list of
edition names corresponding to Forge edition files.

Example:

Ninth Edition
Revised Edition
Ice Age
Homelands

Edition files are expected in:

Data/editions/

EXAMPLE OUTPUT
==============

Checking editions to load...
Compiling source card list...
INFO: Loading Ninth Edition...
INFO: Loading Revised Edition...
INFO: Loading Ice Age...
INFO: Loading Homelands...
INFO: Loading Alliances...
INFO: Loading Time Spiral...
INFO: Loading Ninth edition...
WARNING: Duplicate detected. Skipping Ninth edition.
INFO: Loading Coldsnap...
INFO: Loading Fallen Empires...
INFO: Loading The Dark...
Checking unsupported cards...
INFO: Found 557 unsupported cards.
Loading user-banned cards...
Formatting cards to MTG: Forge format...
INFO: Generating edition codes...
Writing unsupported cards to Standard.txt...
Compilation complete!

PROJECT STRUCTURE
=================

core/
    card_loader.py  
        File parsing and data extraction utilities  

    card_processor.py  
        Core processing and transformation logic  

    const.py  
        Constants and format templates  

DATA UPDATES
============

This tool relies on external data files:

* Forge edition files sourced from MTG: Forge (Data/editions/)
* Shandalar card list sourced from Shandalar (data/Shandalar Card List.csv)

To update data:

1. Replace the existing data files with updated versions from your MTG: Forge installation or other sources.
2. Ensure filenames and structure remain consistent.

No additional configuration is required as long as file structure is preserved.

ROADMAP
=======

v2 (Deck Translator):

* Deck translation between Shandalar and Forge
* Performance improvements (if needed)

v2.5 (Refinement & Flexibility):

* Refinements to existing architecture
* Add header column in user_banned to organize user-generated section headers
* Support for more output formats (i.e. not just "Standard")
* Configure Shandalar data set via params (e.g. "classic" vs. "ProJared")

v3 (Data Updater):

* Sync data from the Forge repository to ensure that new editions are supported automatically

PURPOSE
=======

This project was created to streamline deck building for Shandalar mods
ensuring that decks created in MTG: Forge only contain cards supported by the
game.

It serves as both a practical utility and a demonstration of structured data
processing, error handling, and CLI application design developed through
iterative refinement.

This tool was developed iteratively through real-world use. As new edge cases
and data inconsistencies were encountered (e.g., missing files, encoding issues,
duplicate editions), the design was refined to handle them explicitly and
reliably.

The current structure reflects those iterations, prioritizing clear data flow,
explicit error handling, and separation between CLI, loading, and processing
logic.

In other words: I designed this project for real world use, not to sit in
a Git repository. Expect it to evolve with time.

DESIGN NOTES
============

This project separates data loading, validation, and application control:

* Loader functions may return None when data cannot be found. This allows the
  calling layer to decide whether the input is optional or required.

* Empty collections (e.g., []) represent valid but empty data and are handled
  separately from missing inputs.

* The CLI layer is responsible for validating required inputs and determining
  whether execution should continue or terminate.

* Helper validation functions may terminate execution early (via sys.exit) when
  encountering invalid or missing required data.

* Exceptions are used for malformed or unexpected data, ensuring that invalid
  states do not silently propagate through the system.
