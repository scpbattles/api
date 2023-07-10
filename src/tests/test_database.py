import unittest

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from scpbattlesapi.database import DatabaseHandler
from scpbattlesapi.steamapi import SteamAPI
from scpbattlesapi.yamlhandler import YAMLHandler

class DatabaseTest(unittest.TestCase):
    def setUp(self):

        with YAMLHandler("/etc/scpbattlesapi/config.yaml") as config:
            steam_api_key = config["steam_api_key"]

        steam_api = SteamAPI(steam_api_key)
        
        self.database = DatabaseHandler(
            connection_string="localhost", 
            config_path="/etc/scpbattlesapi/config.yaml", 
            steam_api=steam_api, 
            bad_words_path="/etc/scpbattlesapi/bad_words.json"
        )

        try:
            self.database.mongo_client.admin.command("ping")

        except ConnectionFailure:
            print("Server not available")
    
    def test_default_items(self):

        self.assertEqual(True, False)
        

    def tearDown(self):
        self.mongo_client.close()