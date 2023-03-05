import requests

def get_inventory(steam_id, steam_api_key):

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    parameters = {
        "key": steam_api_key,
        "appid": 2173020,
        "steamid": steam_id
    }

    response = requests.get("https://partner.steam-api.com/IInventoryService/GetInventory/v1/", params=parameters, headers=headers)

    inventory = response.json()["response"]["item_json"]

    return inventory