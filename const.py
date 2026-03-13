# Paths to data folders.
data_path_cards = "Data/cardsfolder"
data_path_editions = "Data/editions"

# Paths to data and config files.
file_shandalar_csv = "Data/Shandalar Card List.csv"
file_config = "config.csv"
file_user_banned = "user_banned.csv"

# CSV column pointers.
editions_card_name_starting_column = 2
shandalar_card_name_column = 0

# MTG Forge format descriptions.
forge_format_body_standard = """[format]
Name:Standard
Order:101
Subtype:Standard
Type:Sanctioned
Banned: {banned_cards}
Sets: {set_codes}"""