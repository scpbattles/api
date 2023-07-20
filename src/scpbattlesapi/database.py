from typing import TypedDict

class Server(TypedDict):

    id: str
    ip: str
    token: str
    owner_discord_id: int
    last_pinged: int
    is_official: bool
    current_foundation: int
    current_coalition: int
    version: str
    max_players: int
    map: str
    mode: "str"
    port: int
    current_players: int

class User(TypedDict):
        steam_id: int
        is_banned: bool
        creation_date: float
        elo: int
        exp: int