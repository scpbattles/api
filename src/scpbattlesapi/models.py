from typing import List, Dict, Type, Union, Tuple
import secrets 
import time 
import random

from scpbattlesapi.steamapi import SteamAPI
from scpbattlesapi.yamlhandler import YAMLHandler

# this is kruz from may 17 2023
# im looking back at this code and realizing how good it is
# models are constructed with parameters loaded from database
# this allows models to exist purely in memory and thus can be created purely in memory
# this means that we can create a new model in memory then save it to the database
# models contain a pointer to the database handler to interface with data that is not specific itself
# this allows us to play with live data from the database without worrying that its out of date

# i remember struggling with this project a lot but i got it so right

# TODO: move this its own file and import it if TYPE_CHECKING
class DatabaseHandler:
    def __init__(self, database_path: str, config_path: str, bad_words_path: str, steam_api: SteamAPI):
        
        self.database_path = database_path
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
        
        with YAMLHandler(self.database_path) as database:

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

        return server

    def save_user(self, user: "User") -> None:
        
        with YAMLHandler(self.database_path) as database:

            database["users"][user.steam_id] = {
                "is_banned": user.is_banned,
                "first_login": user.first_login,
                "token": user.token,
                "token_expiration": user.token_expiration,
                "elo": user.elo,
                "exp": user.exp
            }

    def save_server(self, server: "Server") -> None:
        
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

class Model:
    def __init__(
        self,
        database_handler: DatabaseHandler,
        steam_api: SteamAPI
    ):
        
        self.database_handler = database_handler
        self.steam_api = steam_api

class User(Model):
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
            exp: int
    ):

        super().__init__(database_handler=database_handler, steam_api=steam_api)

        self.steam_id = steam_id
        self.is_banned = is_banned
        self.first_login = first_login
        self.token = token
        self.token_expiration = token_expiration
        self.elo = elo
        self.exp = exp
        
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


    def consume_item(self, item: "Item") -> None:

        self.steam_api.consume_item(
            item_id=item.item_id,
            steam_id=self.steam_id
        )

    def add_item(self, item_def: int) -> None:

        self.steam_api.add_item(
            item_def=item_def,
            steam_id=self.steam_id
        )

    def give_default_items(self) -> None:

        for item in self.database_handler.default_items:
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
    def __init__(self, item_id: int, item_def: int, owner: User, database_handler: DatabaseHandler, steam_api: SteamAPI) -> None:

        super().__init__(database_handler=database_handler, steam_api=steam_api)

        self.item_id = item_id
        self.item_def = item_def
        self.owner = owner

    def consume(self):
        self.owner.consume_item(self)


class Key(Item):
    pass

class Case(Item):

    def __init__(self, item_id: int,
                 item_def: int, owner: User, database_handler: DatabaseHandler, steam_api: SteamAPI) -> None:

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
        database_handler: DatabaseHandler,
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
        self.name = name
    
    def save(self):
        self.database_handler.save_server(self)
    
class InvalidKey(Exception):
    pass

class NotAUser(Exception):
    pass