import tomlkit

steamid = "testingID"

print(f"New user {steamid}")

with open("root/etc/scpbattlesapi/config.toml", "r") as file:
    config = tomlkit.parse(file.read())

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

params = {
    "key": config["steam_api_key"],
}

stupidness = ""

for index, itemdef in enumerate(config["default_items"]):
    stupidness += f"&itemdefid[{index}]={itemdef}"     

data = f"appid=2173020&steamid={steamid}{stupidness}"

print(data)