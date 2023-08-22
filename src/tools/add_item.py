import os
import argparse

from scpbattlesapi.steamapi import SteamAPI

steam = SteamAPI(os.environ.get("SCPBATTLES_STEAM_API_KEY"))

CAIDEN_JONES = 76561199158858596
VOXANY = 76561198081096335
CHALET = 76561199067234943
NOAH = 76561198425783189
LILY = 76561198846629634

for i in range(0,20):
    steam.add_items(52, CAIDEN_JONES)