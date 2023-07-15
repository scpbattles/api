import os
import time
import uuid
import unittest

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from scpbattlesapi.database import DatabaseHandler
from scpbattlesapi.steamapi import SteamAPI
from scpbattlesapi.yamlhandler import YAMLHandler
from scpbattlesapi.models import User, Server

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

        self.assertIsInstance(
            self.database.default_items,
            list
        )
    
    def test_case_probabilities(self):

        self.assertIsInstance(
            self.database.case_probabilites,
            dict
        )
    
    def test_item_model_map(self):

        self.assertIsInstance(
            self.database.item_model_map,
            dict
        )
    
    def test_case_key_map(self):

        self.assertIsInstance(
            self.database.case_key_map,
            dict
        )
    
    def test_fetch_user(self):

        user = self.database.fetch_user(76561198191668608)

        self.assertIsInstance(
            user,
            User
        )

        self.assertIsInstance(
            user.steam_id,
            int
        )

        self.assertIsInstance(
            user.creation_date,
            float
        )

        self.assertIsInstance(
            user.elo,
            int
        )

        self.assertIsInstance(
            user.exp,
            int 
        )

        self.assertIsInstance(
            user.is_banned,
            bool
        )

        self.assertIsInstance(
            user.token,
            str
        )

        self.assertIsInstance(
            user.token_expiration,
            int
        )
    
    def test_fetch_server(self):
        
        server = self.database.fetch_server("test")

        self.assertIsInstance(
            server,
            Server
        )

        self.assertIsInstance(
            server.current_coalition,
            int
        )
        
        self.assertIsInstance(
            server.current_foundation,
            int 
        )

        self.assertIsInstance(
            server.database_handler,
            DatabaseHandler,
        )

        self.assertIsInstance(
            server.id,
            str 
        )

        self.assertIsInstance(
            server.ip,
            str 
        )

        self.assertIsInstance(
            server.token,
            str 
        )

        self.assertIsInstance(
            server.owner_discord_id,
            int
        )

        self.assertIsInstance(
            server.last_pinged,
            float
        )

        self.assertIsInstance(
            server.is_official,
            bool 
        )

        self.assertIsInstance(
            server.version,
            str 
        )
        
        self.assertIsInstance(
            server.max_players,
            int 
        )

        self.assertIsInstance(
            server.map,
            str 
        )

        self.assertIsInstance(
            server.mode,
            str 
        )

        self.assertIsInstance(
            server.port,
            int
        )

    def test_save_user(self):
        
        # we will use this to ensure saving works properly
        token = str(uuid.uuid4())

        test_user = User(
            steam_id=0,
            is_banned=False,
            creation_date=0,
            database_handler=self.database,
            steam_api=self.database.steam_api,
            token=token,
            token_expiration=0,
            elo=0,
            exp=0
        )

        self.database.save_user(test_user)

        test_user = None 

        test_user = self.database.fetch_user(0)

        self.assertEqual(
            test_user.token,
            token
        )        
    
    def test_save_server(self):

        last_pinged = time.time()

        server = Server(
            steam_api=self.database.steam_api,
            database_handler=self.database,
            ip="server.example",
            token=os.environ.get("TEST_SERVER_TOKEN"),
            owner_discord_id=193547000489312256,
            last_pinged=last_pinged,
            is_official=False,
            current_foundation=0,
            current_coalition=0,
            version="0.0.0",
            max_players=0,
            map="example map",
            mode="example mode",
            port=0,
            id="test"
        )

        self.database.save_server(server)

        server = None 

        server = self.database.fetch_server("test")

        self.assertEqual(
            last_pinged,
            server.last_pinged
        )

    def tearDown(self):
        self.database.mongo_client.close()