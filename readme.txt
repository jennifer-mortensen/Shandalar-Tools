SHANDALAR TOOLS
===============

A Python command-line utility for generating MTG Forge format restrictions
compatible with the Shandalar mod.

MTG Forge supports cards from many expansions, but the Shandalar mod only
implements a subset of them. This tool scans Forge edition files and creates a 
format definition that bans cards not supported by Shandalar.

This allows decks to be built in Forge while ensuring they remain compatible
with the Shandalar mod.

FEATURES

* Loads card lists from MTG Forge edition files
* Compares them against the Shandalar card pool
* Generates a Forge format file banning unsupported cards
* Supports optional user ban lists for custom restrictions
* Handles duplicate editions
* Detects file encodings automatically

REQUIREMENTS
============

* Python 3.9+
* chardet

Install dependencies:

* pip install chardet

USAGE
=====

Basic usage:

python cli.py

This will:

* Load editions listed in config.csv
* Compare them against the Shandalar card list
* Generate a Forge format file containing unsupported cards

OPTIONS
=======

-o, --output
Specify the output file.

Example:
python cli.py -o unsupported.txt

-e, --editions
Specify the CSV file listing editions to load.

-b, --user-banned
Specify the CSV file listing user-designated cards to ban.

Example:
python cli.py -e custom_sets.csv

CONFIGURATION
=============

config.csv

Contains a list of edition names corresponding to Forge edition files.

Example:

Ninth Edition
Revised Edition
Ice Age
Homelands

Edition files are expected in:

Data/editions/

EXAMPLE OUTPUT
==============

Compiling source card list...
Loading Ice Age...
Loading Homelands...

Checking unsupported cards...
Found 642 unsupported cards.

Writing unsupported cards to output.txt...
Compilation complete!

PROJECT STRUCTURE
=================

cli.py
Command line interface and main pipeline logic

card_loader.py
File parsing and card extraction utilities

const.py
Constants and format templates

Data/
Shandalar card list and Forge edition files

ROADMAP
=======

Planned improvements:
* Deck translation tool between MTG Forge and Shandalar
* Additional compatibility validation tools
* Improved CLI options and logging
* Additional internal cleanup

PURPOSE
=======

This project was created to streamline deck building for a Shandalar mod by
ensuring that decks created in MTG Forge only contain cards supported by the
game. It was built as a practical tool to automate compatibility checks
between the two systems.