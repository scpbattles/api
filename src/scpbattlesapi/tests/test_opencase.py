from models import *


item_group_probabilities = {
    5999: [43,46,49],
    8499: [47,42,53],
    9499: [48,50,55],
    9899: [45,44,34],
    10000: [54]
}

steam_api = SteamAPI(
    api_key="E6A4346C76567A0152BEF44454E24BAA"
)

user = User(
    steam_id=76561198081096335,
    steam_api=steam_api,
    is_banned=False,
    first_login=0
)

case = Case(
    item_group_probabilities=item_group_probabilities,
    valid_keys=[52],
    item_def=51,
    item_id=4214844247387963661,
    owner=user
)

key = Key(
    item_id=4214844247387902708,
    item_def=52,
    owner=user
)

awarded_item_def = case.open(key)

print(awarded_item_def)