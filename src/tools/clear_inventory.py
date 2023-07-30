import os

from scpbattlesapi.steamapi import SteamAPI

VOXANY = 76561198081096335

steam = SteamAPI(os.environ.get("SCP_BATTLES_STEAM_API_KEY"))

inventory = steam.get_inventory(VOXANY)

for item in inventory:
    if item["itemdefid"] == 1:
        print("TUNA CASSEROLE")
        continue
    
    steam.consume_item(item["itemid"], VOXANY)