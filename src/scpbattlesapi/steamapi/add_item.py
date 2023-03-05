import requests

def add_item(item_def, steam_id, steam_api_key):

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