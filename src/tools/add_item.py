import os
import argparse

from scpbattlesapi.steamapi import SteamAPI

steam = SteamAPI(os.environ.get("STEAM_API_KEY"))

CAIDEN_JONES = 76561199158858596
VOXANY = 76561198081096335
CHALET = 76561199067234943
NOAH = 76561198425783189

for item in range(0, 20):
    steam.add_item(51, NOAH)