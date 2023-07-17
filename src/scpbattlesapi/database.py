import os
from typing import List, Dict, Type, TYPE_CHECKING

from pymongo.mongo_client import MongoClient

from scpbattlesapi.yamlhandler import YAMLHandler
from scpbattlesapi.steamapi import SteamAPI
from scpbattlesapi.models import User, Server, Item

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

    def fetch_users(
        self, 
        steam_id: int = None,
        is_banned: bool = None,
        creation_date: float = None,
        token: str = None,
        token_expiration: float = None,
        elo: int = None,
        exp: int = None
    ) -> List["User"]:

        # this dictionary comprehension takes arguments provided (as a dict) to fetch_server 
        # and removes any with the value of None
        database_query = {k: v for k, v in locals().items() if v is not None}

        # "self" shouldnt be part of the query
        del database_query["self"]

        # convert cursor to list
        matching_user_documents = list(
            self.database.users.find(
                database_query
            )
        )

        if len(matching_user_documents) < 1:
            raise NoMatchingUser(f"no user for query {database_query}")
        
        matching_users = []

        for user_data in matching_user_documents:
        
            user = User(
                database_handler=self,
                steam_api=self.steam_api,
                steam_id=user_data["steam_id"],
                is_banned=user_data["is_banned"],
                creation_date=user_data["creation_date"],
                token=user_data["token"],
                token_expiration=user_data["token_expiration"],
                elo=user_data["elo"],
                exp=user_data["exp"]
            )

            matching_users.append(
                user
            )

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
        
    ) -> List["Server"]:

        # this dictionary comprehension takes arguments provided (as a dict) to fetch_server 
        # and removes any with the value of None
        database_query = {k: v for k, v in locals().items() if v is not None}

        # "self" shouldnt be part of the query
        del database_query["self"]

        # convert cursor to list
        matching_server_documents = list(
            self.database.servers.find(
                database_query
            )
        )

        if len(matching_server_documents) < 1:
            raise NoMatchingServer(f"no server for query {database_query}")
        
        matching_servers = []

        for server_data in matching_server_documents:
            server = Server(
                database_handler=self,
                steam_api=self.steam_api,
                ip=server_data["ip"],
                token=server_data["token"],
                owner_discord_id=server_data["owner_discord_id"],
                last_pinged=server_data["last_pinged"],
                is_official=server_data["is_official"],
                current_foundation=server_data["current_foundation"],
                current_coalition=server_data["current_coalition"],
                version=server_data["version"],
                max_players=server_data["max_players"],
                map=server_data["map"],
                mode=server_data["mode"],
                port=server_data["port"],
                id=server_data["id"],
                current_players=server_data["current_players"]
            )

            matching_servers.append(
                server
            )

        return matching_servers

    def save_user(self, user: "User") -> None:

        self.database.users.find_one_and_replace(
            {"steam_id": user.steam_id},
            {
                "steam_id": user.steam_id,
                "is_banned": user.is_banned,
                "creation_date": user.creation_date,
                "token": user.token,
                "token_expiration": user.token_expiration,
                "elo": user.elo,
                "exp": user.exp
            }, 
            upsert=True
        )
    
    def save_server(self, server: "Server") -> None:
        
        self.database.servers.find_one_and_replace(
            {"id": server.id},
            {
                "ip": server.ip,
                "token": server.token,
                "owner_discord_id": server.owner_discord_id,
                "last_pinged": server.last_pinged,
                "is_official": server.is_official,
                "current_foundation": server.current_foundation,
                "current_coalition": server.current_coalition,
                "version": server.version,
                "max_players": server.max_players,
                "map": server.map,
                "mode": server.mode,
                "port": server.port,
                "id": server.id,
                "current_players": server.current_players
            },
            upsert=True
        )

class NoMatchingUser(Exception):
    pass

class NoMatchingServer(Exception):
    pass