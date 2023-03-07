import time
from typing import Dict, List
import json
import random
import secrets

import requests
from requests import HTTPError

from config import Config
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
            "itemdefid[0]": item_def
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
            steam_api: SteamAPI, 
            default_items: List[int], 
            token: str,
            token_expiration: int,
            elo: int,
            exp: int
        ):

        self.steam_id = steam_id
        self.is_banned = is_banned
        self.first_login = first_login
        self.steam_api = steam_api
        self.default_items = default_items
        self.token = token 
        self.token_expiration = token_expiration
        self.elo = elo
        self.exp = exp

    def get_inventory(self) -> Dict[str, int]:
        inventory = self.steam_api.get_inventory(
            steam_id=self.steam_id
        )

        return inventory

    def consume_item(self, item_id: int) -> None:
        self.steam_api.consume_item(
            item_id=item_id,
            steam_id=self.steam_id
        )

    def add_item(self, item_def: int) -> None:
        self.steam_api.add_item(
            item_def=item_def,
            steam_id=self.steam_id
        )
    
    def give_default_items(self) -> None:

        for item in self.default_items:

            self.add_item(
                item_def=item
            )
        
    def generate_token(self):

        self.token = secrets.token_urlsafe()
        self.token_expiration = int(
            time.time() + (60*30)
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
    def __init__(self, item_group_probabilities: Dict[int, List[int]], valid_keys: List[int], item_id: int, item_def: int, owner: User) -> None:
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
    def __init__(self, ip: str, server_token: str, owner_discord_id: int, last_pinged: int, is_official: bool) -> None:

        self.ip = ip
        self.server_token = server_token
        self.owner_discord_id = owner_discord_id
        self.last_pinged = last_pinged
        self.is_official = is_official

