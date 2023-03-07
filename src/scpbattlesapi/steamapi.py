from typing import Dict
import json

import requests

def add_item(item_def: int, steam_id: int, steam_api_key: str) -> None:

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    parameters = {
        "key": steam_api_key,
        "appid": 2173020,
        "steamid": steam_id,
        "itemdefid[0]": item_def
    }

    response = requests.post('http://api.steampowered.com/IInventoryService/AddItem/v1', params=parameters, headers=headers)

    response.raise_for_status()

def consume_item(item_id: int, steam_id: int, steam_api_key: str) -> None:

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    parameters = {
        "key": steam_api_key,
        "appid": 2173020,
        "itemid": item_id,
        "steamid": steam_id,
        "quantity": "1"
    }

    response = requests.post("https://partner.steam-api.com/IInventoryService/ConsumeItem/v1/", params=parameters, headers=headers)

    response.raise_for_status()

def get_inventory(steam_id: int, steam_api_key: str) -> Dict[str, int]:

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    parameters = {
        "key": steam_api_key,
        "appid": 2173020,
        "steamid": steam_id
    }

    response = requests.get("https://partner.steam-api.com/IInventoryService/GetInventory/v1/", params=parameters, headers=headers)

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