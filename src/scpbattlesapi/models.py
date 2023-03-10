from typing import List, Dict, Type
import secrets 
import time 
import random

from steamapi import SteamAPI

class User:
    def __init__(
            self,
            steam_id: int,
            is_banned: bool,
            first_login: float,
            database_handler: "DatabaseHandler",
            steam_api: SteamAPI,
            token: str,
            token_expiration: int,
            elo: int,
            exp: int,
            default_items: List[int],
            item_model_map: dict
    ):

        self.steam_id = steam_id
        self.is_banned = is_banned
        self.first_login = first_login
        self.steam_api = steam_api
        self.token = token
        self.token_expiration = token_expiration
        self.elo = elo
        self.exp = exp
        self.default_items = default_items
        self.item_model_map = item_model_map
        
    @property
    def inventory(self) -> Dict[int, Type["Item"]]:

        inventory_raw = self.steam_api.get_inventory(
            steam_id=self.steam_id
        )

        #print(type(inventory_raw))

        inventory_processed = {}

        for item_id, item_data in inventory_raw.items():
            
            match item_data["itemdefid"]:
                
                case 51: # case

                    inventory_processed[item_id] = Case(
                        item
                    )

        return inventory_processed

    def consume_item(self, item: "Item") -> None:
        self.steam_api.consume_item(
            item_id=item.item_id,
            steam_id=self.steam_id
        )

    def add_item(self, item_def: int) -> None:
        self.api.steam_api.add_item(
            item_def=item_def,
            steam_id=self.steam_id
        )

    def give_default_items(self) -> None:

        for item in self.default_items:
            self.add_item(
                item_def=item.item_def
            )

    def generate_token(self):

        self.token = secrets.token_urlsafe()
        self.token_expiration = int(
            time.time() + (60 * 30)
        )

    def reset_inventory(self):

        inventory = self.get_inventory()

        for item in inventory.values():
            self.consume_item(
                item.item_id
            )

        self.give_default_items()


class Item:
    def __init__(self, item_id: int, item_def: int, owner: User) -> None:
        self.item_id = item_id
        self.item_def = item_def
        self.owner = owner

    def consume(self):
        self.owner.consume_item(self)


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
        steam_api: SteamAPI,
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
        
        self.steam_api = steam_api
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
    
class InvalidKey(Exception):
    pass