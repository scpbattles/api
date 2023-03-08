from models import *

api = SCPBattlesAPI(database_path="database.yaml", config_path="config.yaml")

user = User(
    api=api,
    steam_id=76561198081096335,
    is_banned=False,
    first_login=1645489437.0773406,
    token=None,
    token_expiration=0,
    elo=420,
    exp=421
)

server = Server(
    api=api,
    ip="127.0.0.1",
    token="a token!!!",
    owner_discord_id=3498934,
    last_pinged=909324023,
    is_official=False,
    current_coalition=2,
    current_foundation=4,
    version="12545",
    max_players=2000,
    map="COol!",
    mode="A cool mode!",
    port=234,
    name="EPIC SERVERRRR"
)

user.save()

server.save()