import requests
from time import sleep

user = {
    "username": "Voxany",
    "password": "password",
    "email": "kruzerbroek@gmail.com",
    "elo": "500000",
    "banned": False,
    "agreed_toc": True,
    "over_13": True
}

my_server = {
    "server_name": "Epic Server!",
    "players": 0,
    "max_players": 10,
}

account = {
    "username": "kruz",
    "password": "password"
}

#response = requests.put("http://voxany.io/servers/kruz", json = my_server, headers = {"auth_id": "kUgZHgGDNAKdCNoToBGpHQMAHacLZWW"})

response = requests.get("http://voxany.io/generate_token", json = {"username": "admin", "password": "admin"})

print(response.text)

print(response.headers)
