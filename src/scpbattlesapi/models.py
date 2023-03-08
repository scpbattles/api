import time
from typing import Dict, List, Union
import json
import random
import secrets

import requests
from requests import HTTPError

from config import Config
from database import Database
from exceptions import InvalidKey, FailedToConsume


class SteamAPI:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_inventory(self, steam_id: int) -> Dict[str, int]:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        parameters = {
            "key": self.api_key,
            "appid": 2173020,
            "steamid": steam_id
        }

        response = requests.get("https://partner.steam-api.com/IInventoryService/GetInventory/v1/", params=parameters,
                                headers=headers)

        response.raise_for_status()

        inventory = json.loads(
            response.json()["response"]["item_json"]
        )

        parsed_inventory = []

        for item in inventory:
            parsed_inventory.append(
                {
                    "itemid": int(item["itemid"]),
                    "quantity": item["quantity"],
                    "itemdefid": int(item["itemdefid"])
                }
            )

        return parsed_inventory

    def consume_item(self, item_id: int, steam_id: int) -> None:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        parameters = {
            "key": self.api_key,
            "appid": 2173020,
            "itemid": item_id,
            "steamid": steam_id,
            "quantity": "1"
        }

        response = requests.post("https://partner.steam-api.com/IInventoryService/ConsumeItem/v1/", params=parameters,
                                 headers=headers)

        # response.json() doesnt fully deserialize the json
        consumed_items = json.loads(
            response.json()["response"]["item_json"]
        )

        if len(consumed_items) == 0:
            raise FailedToConsume()

        response.raise_for_status()

    def add_item(self, item_def: int, steam_id: int) -> None:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        parameters = {
            "key": self.api_key,
            "appid": 2173020,
            "steamid": steam_id,
            "itemdef id[0]": item_def
        }

        response = requests.post('http://api.steampowered.com/IInventoryService/AddItem/v1', params=parameters,
                                 headers=headers)

        response.raise_for_status()

class User:
    def __init__(
            self,
            steam_id: int,
            is_banned: bool,
            first_login: float,
            api: "SCPBattlesAPI",
            token: str,
            token_expiration: int,
            elo: int,
            exp: int
    ):

        self.steam_id = steam_id
        self.is_banned = is_banned
        self.first_login = first_login
        self.api = api
        self.token = token
        self.token_expiration = token_expiration
        self.elo = elo
        self.exp = exp

    def save(self):

        self.api.save(self)
        
    @property
    def inventory(self) -> Dict[str, int]:

        inventory = self.api.steam_api.get_inventory(
            steam_id=self.steam_id
        )

        return inventory

    def consume_item(self, item_id: int) -> None:
        self.api.steam_api.consume_item(
            item_id=item_id,
            steam_id=self.steam_id
        )

    def add_item(self, item_def: int) -> None:
        self.api.steam_api.add_item(
            item_def=item_def,
            steam_id=self.steam_id
        )

    def give_default_items(self) -> None:

        for item in self.api.default_items:
            self.add_item(
                item_def=item
            )

    def generate_token(self):

        self.token = secrets.token_urlsafe()
        self.token_expiration = int(
            time.time() + (60 * 30)
        )

    def reset_inventory(self):

        inventory = self.get_inventory()

        for item in inventory:
            self.consume_item(
                item["itemid"]
            )

        self.give_default_items()


class Item:
    def __init__(self, item_id: int, item_def: int, owner: User) -> None:
        self.item_id = item_id
        self.item_def = item_def
        self.owner = owner

    def consume(self):
        self.owner.consume_item(self.item_id)


class Key(Item):
    pass

class Case(Item):

    def __init__(self, item_group_probabilities: Dict[int, List[int]], valid_keys: List[int], item_id: int,
                 item_def: int, owner: User) -> None:

        super().__init__(item_id, item_def, owner)

        self.valid_keys = valid_keys

        self.item_group_probabilities = item_group_probabilities

    def open(self, key: Key) -> int:

        if key.item_def not in self.valid_keys:
            raise InvalidKey()

        key.consume()

        self.consume()

        awarded_item_def = self.roll()

        self.owner.add_item(
            item_def=awarded_item_def
        )

        return awarded_item_def

    def roll(self) -> int:

        random_number = random.randint(1, 10000)

        for random_number_height, possible_items in self.item_group_probabilities.items():

            if random_number <= random_number_height:

                possible_items = possible_items

                break

            else:
                continue

        awarded_item_def = random.choice(possible_items)

        return awarded_item_def


class Server:
    def __init__(
        self,
        api: "SCPBattlesAPI",
        ip: str, 
        token: str, 
        owner_discord_id: int, 
        last_pinged: int, 
        is_official: bool,
        current_foundation: int,
        current_coalition: int,
        version: str, 
        max_players: int,
        map: str, 
        mode: str,
        port: int,
        name: str
    ) -> None:
        
        self.api = api
        self.ip = ip
        self.token = token
        self.owner_discord_id = owner_discord_id
        self.last_pinged = last_pinged
        self.is_official = is_official
        self.current_foundation = current_foundation
        self.current_coalition = current_coalition
        self.version = version
        self.max_players = max_players
        self.map = map
        self.mode = mode 
        self.port = port 
        self.name = name
    
    def save(self):
        
        self.api.save(self)
    
class SCPBattlesAPI:
    def __init__(self, database_path: str, config_path: str, steam_api: SteamAPI = None):
        
        self.database_path = database_path
        self.config_path = config_path

        # try to make SteamAPI object if not provided
        if steam_api is None:
            with Config(self.config_path) as config:
                steam_api_key = config["steam_api_key"]
            
            self.steam_api = SteamAPI(steam_api_key)

    @property
    def default_items(self):
        with Config(config_path=self.config_path) as config:
            default_items = config["default_items"]
        
        return default_items

    def save(self, model: Union[User, Server]) -> None:

        model_type = type(model)
        
        # would use match statement but pylance doesnt like it
        if model_type is User:
            self._save_user(model)
        
        elif model_type is Server:
            self._save_server(model)

    def _save_user(self, user: User) -> None:
        
        with Database(self.database_path) as database:

            database["users"][user.steam_id] = {
                "is_banned": user.is_banned,
                "first_login": user.first_login,
                "token": user.token,
                "token_expiration": user.token_expiration,
                "elo": user.elo,
                "exp": user.exp
            }

    def _save_server(self, server: Server) -> None:
        
        with Database(self.database_path) as database:

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

    def fetch_user(self, steam_id: int) -> User:
        with Database(self.database_path) as database:
            user_data = database["users"][steam_id]

        user = User(
            steam_id=steam_id,
            is_banned=user_data["is_banned"],
            first_login=user_data["first_login"],
            api=self,
            token=user_data["token"],
            token_expiration=user_data["token_expiration"],
            elo=user_data["elo"],
            exp=user_data["exp"]
        )

        return user

    def fetch_server(self, server_id: str) -> Server:

        with Database(self.database_path) as database:
            server_data = database["servers"][server_id]
        
        server = Server(
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

