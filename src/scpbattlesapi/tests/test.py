from models import DatabaseHandler, User, Server, Case 
from steamapi import SteamAPI

steam_api = SteamAPI("E6A4346C76567A0152BEF44454E24BAA")

database_handler = DatabaseHandler(database_path="test_database.yaml", config_path="test_config.yaml", steam_api=steam_api)

user = database_handler.fetch_user(76561198081096335)

inventory = user.inventory

print(inventory)

key = inventory[4212593081292708990]
case = inventory[4212593081292717064]

awarded_item = case.open(key)

print(awarded_item)