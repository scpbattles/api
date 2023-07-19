import json
from typing import Dict, TypedDict, List

import requests
from requests import JSONDecodeError

class FailedToConsume(Exception):
    pass

class FailedToAdd(Exception):
    pass 

class Item(TypedDict):
    itemid: int
    quantity: int
    itemdefid: int 

class SteamAPI:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_inventory(self, steam_id: int) -> List[Item]:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        parameters = {
            "key": self.api_key,
            "appid": 2173020,
            "steamid": steam_id
        }

        response = requests.get(f"https://partner.steam-api.com/IInventoryService/GetInventory/v1/", params=parameters,
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
                    "quantity": int(item["quantity"]),
                    "itemdefid": int(item["itemdefid"]) 
                }
            )

        return parsed_inventory

    def query_inventory(self, steam_id: int, query: Item, inventory = None) -> List[Item]:
        """
        Search a user's inventory for items with certain attributes
        """
        
        # allows passing an inventory directly to prevent inventory fetches
        if not inventory:
            inventory = self.get_inventory(steam_id)

        matching_items = []

        for item in inventory:
            if set(query.items()).issubset(set(item.items())):
                matching_items.append(item)
        
        return matching_items

        

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

        try:
            response.json()
        except JSONDecodeError:
            # when it fails to add items it sends up messed json for some god forsaken reason
            raise FailedToAdd()


        response.raise_for_status()
    
