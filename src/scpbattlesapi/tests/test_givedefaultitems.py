from scpbattlesapi.models import *

steam_api = SteamAPI(
    api_key="E6A4346C76567A0152BEF44454E24BAA"
)

user = User(
    steam_id=76561199484408739,
    token_expiration=0,
    token=0,
    steam_api=steam_api,
    is_banned=False,
    first_login=0,
    default_items= [2,3,4,5,6,7,39,41,40,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27],
    elo=20,
    exp=20
)

user.give_default_items()