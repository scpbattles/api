from typing import List, Dict, Type, Union, Tuple, TYPE_CHECKING
import secrets 
import time 
import random

from scpbattlesapi.steamapi import SteamAPI
from scpbattlesapi.yamlhandler import YAMLHandler

if TYPE_CHECKING:
    from scpbattlesapi.database import DatabaseHandler

# this is kruz from may 17 2023
# im looking back at this code and realizing how good it is
# models are constructed with parameters loaded from database
# this allows models to exist purely in memory and thus can be created purely in memory
# this means that we can create a new model in memory then save it to the database
# models contain a pointer to the database handler to interface with data that is not specific itself
# this allows us to play with live data from the database without worrying that its out of date

# i remember struggling with this project a lot but i got it so right

class Model:
    def __init__(
        self,
        database_handler: "DatabaseHandler",
        steam_api: SteamAPI
    ):
        
        self.database_handler = database_handler
        self.steam_api = steam_api

class User(Model):
    def __init__(
            self,
            steam_id: int,
            is_banned: bool,
            creation_date: float,
            database_handler: "DatabaseHandler",
            steam_api: SteamAPI,
            token: str,
            token_expiration: int,
            elo: int,
            exp: int
    ):

        super().__init__(database_handler=database_handler, steam_api=steam_api)

        self.steam_id = steam_id
        self.is_banned = is_banned
        self.creation_date = creation_date
        self.token = token
        self.token_expiration = token_expiration
        self.elo = elo
        self.exp = exp
    
    def save(self):
        self.database_handler.save_user(self)

    @property
    def inventory(self) -> Dict[int, Type["Item"]]:

        inventory_raw = self.steam_api.get_inventory(
            steam_id=self.steam_id
        )

        item_model_map = self.database_handler.item_model_map

        inventory_processed = {}

        for item_id, item_data in inventory_raw.items():
            
            try:
                model_type = item_model_map[item_data["itemdefid"]]

            except KeyError:

                model_type = "Item"
            
            match model_type:

                case "Case":

                    item = Case(
                        item_id=item_data["itemid"],
                        item_def=item_data["itemdefid"],
                        owner=self,
                        database_handler=self.database_handler,
                        steam_api=self.steam_api
                    )
                
                case "Key":

                    item = Key(
                        item_id=item_data["itemid"],
                        item_def=item_data["itemdefid"],
                        database_handler=self.database_handler,
                        steam_api=self.steam_api,
                        owner=self

                    )
                
                case "Item":
                    
                    item = Item(
                        item_id=item_data["itemid"],
                        item_def=item_data["itemdefid"],
                        owner=self,
                        database_handler=self.database_handler,
                        steam_api=self.steam_api
                    )
                
            inventory_processed[int(item_id)] = item
            
        return inventory_processed


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

        for item in self.database_handler.default_items:
            item: Item
            self.add_item(
                item_def=item.item_def
            )

    def generate_token(self):

        self.token = secrets.token_urlsafe()
        self.token_expiration = int(
            time.time() + (60 * 30)
        )

    def reset_inventory(self):

        inventory = self.inventory
        
        for item in inventory.values():
            self.consume_item(
                item.item_id
            )

        self.give_default_items()


class Item(Model):
    def __init__(self, item_id: int, item_def: int, owner: User, database_handler: "DatabaseHandler", steam_api: SteamAPI) -> None:

        super().__init__(database_handler=database_handler, steam_api=steam_api)

        self.item_id = item_id
        self.item_def = item_def
        self.owner = owner

    def consume(self):
        self.owner.consume_item(self.item_id)


class Key(Item):
    pass

class Case(Item):

    def __init__(self, item_id: int,
                 item_def: int, owner: User, database_handler: "DatabaseHandler", steam_api: SteamAPI) -> None:

        super().__init__(item_id, item_def, owner, database_handler, steam_api=steam_api)

    def open(self, key: Key) -> Tuple[int, int]:

        if key.item_def not in self.database_handler.case_key_map[self.item_def]:
            raise InvalidKey()

        key.consume()

        self.consume()

        awarded_item_def, random_number = self.roll()

        self.owner.add_item(
            item_def=awarded_item_def
        )

        return (awarded_item_def, random_number)

    def roll(self) -> int:

        random_number = random.randint(1, 10000)

        for random_number_height, possible_items in self.database_handler.case_probabilites[self.item_def].items():

            if random_number <= random_number_height:

                possible_items = possible_items

                break

            else:
                continue

        awarded_item_def = random.choice(possible_items)

        return (awarded_item_def, random_number)


class Server(Model):
    def __init__(
        self,
        steam_api: SteamAPI,
        database_handler: "DatabaseHandler",
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
        id: str,
        current_players: int

    ) -> None:
        
        super().__init__(database_handler=database_handler, steam_api=steam_api)

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
        self.id = id
        self.current_players = current_players
    
    def save(self):
        self.database_handler.save_server(self)
    
class InvalidKey(Exception):
    pass