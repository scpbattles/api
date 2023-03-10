from models import User, Server, Case 
from steamapi import SteamAPI
from databasehandler import DatabaseHandler

steam_api = SteamAPI("E6A4346C76567A0152BEF44454E24BAA")

database_handler = DatabaseHandler(database_path="test_database.yaml", config_path="test_config.yaml", steam_api=steam_api)

user = database_handler.fetch_user(76561198081096335)

for item in user.inventory.values():
    print(type(item))