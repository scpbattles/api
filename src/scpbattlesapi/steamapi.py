import json
from typing import Dict

import requests

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

        response = requests.get(f"https://partner.steam-api.com/IInventoryService/GetInventory/v1/", params=parameters,
                                headers=headers)
        
        response.raise_for_status()

        inventory = json.loads(
            response.json()["response"]["item_json"]
        )

        parsed_inventory = {}

        for item in inventory:
            parsed_inventory[item["itemid"]] = {
                "itemid": int(item["itemid"]),
                "quantity": item["quantity"],
                "itemdefid": int(item["itemdefid"])
            }

        
        #print(parsed_inventory)

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
    
class FailedToConsume(Exception):
    pass