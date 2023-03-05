import requests

def consume_item(item_id, steam_id, steam_api_key):

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    parameters = {
        "key": steam_api_key,
        "appid": 2173020,
        "itemid": item_id,
        "steamid": steam_id
    }

    response = requests.post("https://partner.steam-api.com/IInventoryService/ConsumeItem/v1/", params=parameters, headers=headers)

    print(response.json())
    print(response.status_code)
    
    return response.text