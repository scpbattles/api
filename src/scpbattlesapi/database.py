import os
from typing import List, Dict, Type, TYPE_CHECKING, Literal, TypedDict

from pymongo.mongo_client import MongoClient

from scpbattlesapi.yamlhandler import YAMLHandler
from scpbattlesapi.steamapi import SteamAPI

class Server(TypedDict):

    id: str
    ip: str
    token: str
    owner_discord_id: int
    last_pinged: int
    is_official: bool
    current_foundation: int
    current_coalition: int
    version: str
    max_players: int
    map: str
    mode: "str"
    port: int
    current_players: int

class User(TypedDict):
        steam_id: int
        is_banned: bool
        creation_date: float
        token: str
        token_expiration: float
        elo: int
        exp: int

class DatabaseHandler:
    def __init__(self, connection_string: str, config_path: str, bad_words_path: str, steam_api: SteamAPI):
        
        self.mongo_client = MongoClient(connection_string)
        self.database = self.mongo_client.scpbattles

        if not os.path.exists(config_path):
            raise FileNotFoundError("Specified config file path does not exist")
        
        if not os.path.exists(bad_words_path):
            raise FileNotFoundError("Specified bad words file path does not exist")
        
        self.config_path = config_path
        self.bad_words_path = bad_words_path
        self.steam_api = steam_api
    
    @property
    def default_items(self) -> List[int]:
        with YAMLHandler(self.config_path) as config:
            default_items = config["default_items"]

        return default_items
    
    @property
    def case_probabilites(self) -> Dict[int, Dict[int, int]]:
        with YAMLHandler(self.config_path) as config:
            case_probabilities = config["case_probabilities"]
        
        return case_probabilities
    
    @property
    def item_model_map(self) -> Dict[int, Type["Item"]]:

        with YAMLHandler(self.config_path) as config:
            item_model_map = config["item_model_map"]

        return item_model_map

    @property
    def case_key_map(self) -> Dict[int, List[int]]:
        with YAMLHandler(self.config_path) as config:
            case_key_map = config["case_key_map"]
        
        return case_key_map
    
    @property
    def crafting_recipes(self) -> Dict[int, List[int]]:
        with YAMLHandler(self.config_path) as config:
            crafting_recipes = config["crafting_recipes"]
        
        return crafting_recipes

    def fetch_users(
        self, 
        steam_id: int = None,
        is_banned: bool = None,
        creation_date: float = None,
        token: str = None,
        token_expiration: float = None,
        elo: int = None,
        exp: int = None
    ) -> List[User]:

        # this dictionary comprehension takes arguments provided (as a dict) to fetch_server 
        # and removes any with the value of None
        database_query = {k: v for k, v in locals().items() if v is not None}

        # "self" shouldnt be part of the query
        del database_query["self"]

        # convert cursor to list
        matching_users = list(
            self.database.users.find(
                database_query
            )
        )

        if len(matching_users) < 1:
            raise NoMatchingUser(f"no user for query {database_query}")
        
        return matching_users
    
    def fetch_servers(
        self,
        id: str = None,
        ip: str = None,
        token: str = None,
        owner_discord_id: int = None,
        last_pinged: int = None,
        is_official: bool = None,
        current_foundation: int = None,
        current_coalition: int = None,
        version: str = None,
        max_players: int = None,
        map: str = None,
        mode: "str" = None,
        port: int = None,
        current_players: int = None
        
    ) -> List[Server]:

        # this dictionary comprehension takes arguments provided (as a dict) to fetch_server 
        # and removes any with the value of None
        database_query = {k: v for k, v in locals().items() if v is not None}

        # "self" shouldnt be part of the query
        del database_query["self"]

        # convert cursor to list
        matching_servers = list(
            self.database.servers.find(
                database_query
            )
        )

        if len(matching_servers) < 1:
            raise NoMatchingServer(f"no server for query {database_query}")
        
        matching_servers = []

        return matching_servers

    def save_user(self, user: "User") -> None:
        
        """
        Update or create user
        
        New users must fill all fields
        """
    
class NoMatchingUser(Exception):
    pass

class NoMatchingServer(Exception):
    pass