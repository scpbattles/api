from steamapi import SteamAPI

steam_api = SteamAPI(
    api_key="E6A4346C76567A0152BEF44454E24BAA"
)


default_items =  [
    2,
    3,
    4,
    5,
    6,
    7,
    39,
    41,
    40,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27
]

for item in default_items:
    steam_api.add_item(
        steam_id=76561199484408739,
        item_def=item

    )