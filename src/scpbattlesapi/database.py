from typing import List, Dict, Type, TYPE_CHECKING

from pymongo.mongo_client import MongoClient

from scpbattlesapi.yamlhandler import YAMLHandler
from scpbattlesapi.steamapi import SteamAPI
from scpbattlesapi.models import User, Server, Item

class DatabaseHandler:
    def __init__(self, connection_string: str, config_path: str, bad_words_path: str, steam_api: SteamAPI):
        
        self.database = MongoClient(connection_string).scpbattles
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

    def fetch_user(self, steam_id: int) -> "User":
        
        with YAMLHandler(self.connection_string) as database:

            try:
                user_data = database["users"][steam_id]
            except KeyError:
                raise NotAUser()
        
        user = User(
            steam_id=steam_id,
            is_banned=user_data["is_banned"],
            first_login=user_data["first_login"],
            steam_api=self.steam_api,
            token=user_data["token"],
            token_expiration=user_data["token_expiration"],
            elo=user_data["elo"],
            exp=user_data["exp"],
            database_handler=self
        )

        return user
    
    def fetch_server(self, server_id: str) -> "Server":

        with YAMLHandler(self.connection_string) as database:
            
            server_data = database[server_id]
        
        server = Server(
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
            name=server_data["name"]
        )

        return server

    def save_user(self, user: "User") -> None:
        
        with YAMLHandler(self.connection_string) as database:

            database["users"][user.steam_id] = {
                "is_banned": user.is_banned,
                "first_login": user.first_login,
                "token": user.token,
                "token_expiration": user.token_expiration,
                "elo": user.elo,
                "exp": user.exp
            }

    def save_server(self, server: "Server") -> None:
        
        with YAMLHandler(self.connection_string) as database:

            database["servers"][server.name] = {
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
                "name": server.name
            }

class NotAUser(Exception):
    pass