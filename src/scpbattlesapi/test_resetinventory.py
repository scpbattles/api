from steamapi import SteamAPI

steam_api = SteamAPI(
    api_key="E6A4346C76567A0152BEF44454E24BAA"
)

inventory = steam_api.fetch_inventory(
    steam_id=76561199484408739,
)

for item in inventory:
    steam_api.consume_item(
        item["itemid"],
        steam_id=76561199484408739
    )