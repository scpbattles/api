from typing import Union

from steamapi import SteamAPI
from yamlhandler import YAMLHandler
from models import User, Server

class DatabaseHandler: # <-- Not sure if this is the best name
    def __init__(self, database_path: str, config_path: str, steam_api: SteamAPI):
        
        self.database_path = database_path
        self.config_path = config_path
        self.steam_api = steam_api
    
    def fetch_user(self, steam_id: int) -> User:
        
        with YAMLHandler(self.database_path) as database:

            try:
                user_data = database["users"][steam_id]
            except KeyError:
                raise NotAUser()

        with YAMLHandler(self.config_path) as config:

            default_items = config["default_items"]
        
        user = User(
            steam_id=steam_id,
            is_banned=user_data["is_banned"],
            first_login=user_data["first_login"],
            steam_api=self.steam_api,
            token=user_data["token"],
            token_expiration=user_data["token_expiration"],
            elo=user_data["elo"],
            exp=user_data["exp"],
            default_items=default_items
        )

        return user
    
    def fetch_server(self, server_id: str) -> Server:

        with YAMLHandler(self.database_path) as database:
            
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

    def save(self, model: Union[User, Server]) -> None:

        model_type = type(model)
        
        # would use match statement but pylance doesnt like it
        if model_type is User:
            self._save_user(model)
        
        elif model_type is Server:
            self._save_server(model)

    def _save_user(self, user: User) -> None:
        
        with YAMLHandler(self.database_path) as database:

            database["users"][user.steam_id] = {
                "is_banned": user.is_banned,
                "first_login": user.first_login,
                "token": user.token,
                "token_expiration": user.token_expiration,
                "elo": user.elo,
                "exp": user.exp
            }

    def _save_server(self, server: Server) -> None:
        
        with YAMLHandler(self.database_path) as database:

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