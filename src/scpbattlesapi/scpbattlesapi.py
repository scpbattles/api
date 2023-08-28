import os
from typing import Dict, List
import random
import time

import docker 
import flask
from flask import request, make_response, jsonify
from pymongo import MongoClient
from requests import HTTPError

from scpbattlesapi.config import ConfigHandler
from scpbattlesapi.steamapi import SteamAPI, Item, FailedToAdd, FailedToConsume
from scpbattlesapi import database

class SCPBattlesAPI:
    def __init__(self):
        
        
        self.db = MongoClient(os.environ.get("SCPBATTLES_MONGODB_ADDRESS")).scpbattles
        self.config = ConfigHandler("/etc/scpbattlesapi/config.yaml", "/etc/scpbattlesapi/bad_words.json")
        self.steam = SteamAPI(os.environ.get("SCPBATTLES_STEAM_API_KEY"))
        self.docker_client = docker.from_env()

        self.server_instances = []

    @staticmethod
    def roll(random_number: int, probabilities: Dict[int, List[int]]) -> int:
        for random_number_height, possible_results in probabilities.items():

            if random_number <= random_number_height:

                possible_results = possible_results

                break

            else:
                continue
        
        if possible_results == []:
            result = None

        else:
            result = random.choice(possible_results)

        return result

    def unbox(self):
        steam_id = request.args.get("steam_id", type=int)
        key_item_id = request.args.get("key_item_id", type=int)
        case_item_id = request.args.get("case_item_id", type=int)

        if not steam_id: return make_response("missing steam_id query parameter", 400).headers.set("Reponse-Type", "open_case")
        if not key_item_id: return make_response("missing key_item_id query parameter", 400).headers.set("Reponse-Type", "open_case")
        if not case_item_id: return make_response("missing case_item_id query parameter", 400).headers.set("Reponse-Type", "open_case")
        
        user = self.db.users.find_one({"steam_id": steam_id})

        if not user: return make_response(f"user {steam_id} not in database")

        inventory = self.steam.get_inventory(steam_id)

        if len(self.steam.query_inventory(steam_id, {"itemid": case_item_id}, inventory=inventory)) < 1: 
            response = make_response("case not in inventory", 404); response.headers["Response-Type"] = "open_case"; return response

        if len(self.steam.query_inventory(steam_id, {"itemid": key_item_id}, inventory=inventory)) < 1:
            response = make_response("key not in inventory", 404); response.headers["Response-Type"] = "open_case"; return response
        
        case: Item = self.steam.query_inventory(steam_id, {"itemid": case_item_id}, inventory=inventory)[0]
        key: Item = self.steam.query_inventory(steam_id, {"itemid": key_item_id}, inventory=inventory)[0]

        if case["itemdefid"] not in self.config.case_key_map.keys():
            response = make_response("specified case is not a case", 404); response.headers["Response-Type"] = "open_case"; return response

        if key["itemdefid"] not in self.config.case_key_map[case["itemdefid"]]:
            response = make_response(f"specified key {key['itemdefid']} is not valid for case {case['itemdefid']}", 404); response.headers["Response-Type"] = "open_case"; return response

        try:
            self.steam.consume_item(case["itemid"], steam_id)
        except FailedToConsume:
            response = make_response(f"failed to consume case {case_item_id}", 424); response.headers["Response-Type"] = "open_case"; return response
        except HTTPError:
            response = make_response(f"steam api error trying to consume case {case_item_id}", 424); response.headers["Response-Type"] = "open_case"; return response
        
        try:
            self.steam.consume_item(key["itemid"], steam_id)
        except FailedToConsume:
            response = make_response(f"failed to consume key {key_item_id}", 424); response.headers["Response-Type"] = "open_case"; return response
        except HTTPError:
            response = make_response(f"steam api error trying to consume key {key_item_id}", 424); response.headers["Response-Type"] = "open_case"; return response
        
        case_random_number = random.randint(1, 10001)

        awarded_item_def = self.roll(case_random_number, self.config.case_probabilites[case["itemdefid"]])

        bonus_random_number = random.randint(1, 10001)

        awarded_bonus_item_def = self.roll(bonus_random_number, self.config.bonus_item_probabilities)

        # list of items to add to inventory
        items_to_add = []
        items_to_add.append(awarded_item_def)
        if awarded_bonus_item_def: items_to_add.append(awarded_bonus_item_def)

        try:
            self.steam.add_items(items_to_add, steam_id)
        except FailedToAdd:
            response = make_response(f"failed to confirm add items", 424); response.headers["Response-Type"] = "open_case"; return response
        except HTTPError:
            response = make_response(f"steam api error trying to add items", 424); response.headers["Response-Type"] = "open_case"; return response
        
        response = make_response(
            jsonify(
                {
                    "awarded_item": awarded_item_def,
                    "awarded_bonus_item": awarded_bonus_item_def,
                    "random_number": case_random_number
                }
            )
        )

        response.headers["Response-Type"] = "open_case"

        return response
    
    def craft(self):
        material_item_defs = request.args.getlist("material", type=int)
        steam_id = request.args.get("steam_id", type=int)

        if len(material_item_defs) == 0: response = make_response("missing or invalid materials", 400); response.headers["Response-Type"] = "crafting"; return response
        
        if steam_id == None: response = make_response("missing or invalid steam_id query parameter", 400); response.headers["Response-Type"] = "crafting"; return response

        result_item_def = None

        # find the matching result_item_id for given crafting materials
        for possible_result_item_def, required_material_item_defs in self.config.crafting_recipes.items(): 
            if set(material_item_defs) == set(required_material_item_defs):
                result_item_def = possible_result_item_def
            
        if result_item_def == None: response = make_response("no result item from given materials", 404); response.headers["Response-Type"] = "crafting"; return response

        user = self.db.users.find_one(
            {"steam_id": steam_id}
        )
        
        if not user: response = make_response(f"no user in database with steam_id {steam_id}", 404); response.headers["Response-Type"] = "crafting"; return response

        items_to_be_consumed = []

        for material_item_def in material_item_defs:
            matching_items = self.steam.query_inventory(steam_id, {"itemdefid": material_item_def})

            if len(matching_items) < 1: response = make_response(f"user does not have item {material_item_def}", 404); response.headers["Response-Type"] = "crafting"; return response
            
            items_to_be_consumed.append(matching_items[0]["itemid"])
        
        for item_id in items_to_be_consumed:

            try:
                self.steam.consume_item(item_id, steam_id)
            except FailedToConsume:
                response = make_response(f"failed to confirm consumption of {item_id}", 424); response.headers["Response-Type"] = "crafting"; return response
            except HTTPError:
                response = make_response(f"steam api error trying to consume {item_id}", 424); response.headers["Response-Type"] = "crafting"; return response
        
        try:
            self.steam.add_items([result_item_def], steam_id)
        except FailedToAdd:
            response = make_response(f"failed to add {item_id} to inventory", 424); response.headers["Response-Type"] = "crafting"; return response
        except HTTPError:
            response = make_response(f"steam api error trying to add {item_id} to inventory", 424); response.headers["Response-Type"] = "crafting"; return response

        response = make_response(str(result_item_def), 201); response.headers["Response-Type"] = "crafting"; return response

    def register_sever(self):
        pass 

    def delete_server(self):
        pass 

    def get_online_servers(self):

        online_servers: List[database.Server] = self.db.servers.find(
            # find any server that has pinged in the last 10 seconds
            {"last_pinged" : {"$gte": time.time() - 10}}
        )

        servers_dict = {}

        # this is stupid but i need to do it for compatibility :(
        for server in online_servers:
            servers_dict[server["id"]] = {
                "name": server["id"],
                "ip": server["ip"],
                "port": server["port"],
                "current_coalition": server["current_coalition"],
                "current_foundation": server["current_foundation"],
                "max_players": server["max_players"],
                "official": server["is_official"],
                "map": server["map"],
                "mode": server["mode"],
                "version": server["version"],
                "current_players": server["current_players"]
            }

        response = make_response(
            servers_dict,
            200
        )

        response.headers["Response-Type"] = "get_server_list"

        return response
    
    def update_server_listing(self, server_id: str):

        auth_token = request.args.get("auth_token", type=str)
        official_server_token = request.args.get("official_auth_token", type=str)
        ip = request.args.get("ip", type=str)
        port = request.args.get("port", type=int)
        map = request.args.get("map", type=str)
        mode = request.args.get("mode", type=str)
        current_players = request.args.get("current_players", type=int)
        max_players = request.args.get("max_players", type=int)
        version = request.args.get("version", type=str)
    
        server: database.Server = self.db.servers.find_one(
            {"id": server_id}
        )

        if not server: response = make_response(f"no such server {server_id}", 404); response.headers.set("Reponse-Type", "update_server"); return response 
        
        if server["token"] != auth_token: response = make_response("invalid server auth token", 401); response.headers.set("Reponse-Type", "update_server"); return response

        if official_server_token == os.environ.get("SCPBATTLES_OFFICIAL_SERVER_TOKEN"): 
            server["is_official"] = True 

        else:
            server["is_official"] = False

        if ip: server["ip"] = ip
        if port: server["port"] = port 
        if map: server["map"] = map
        if mode: server["mode"] = mode 
        if current_players: server["current_players"] = current_players
        if max_players: server["max_players"] = max_players
        if version: server["version"] = version

        server["last_pinged"] = time.time()

        self.db.servers.find_one_and_replace(
            {"id": server_id},
            server
        )

        response = make_response("success", 200); response.headers.set("Reponse-Type", "update_server"); return response

    def give_default_items(self, steamid: int):

        inventory = self.steam.get_inventory(steamid)

        # extract only owned item defs
        inventory_item_defs: List[int] = []

        for item in inventory:
            inventory_item_defs.append(item["itemdefid"])

        needed_items = []

        for default_item in self.config.default_items:
            if default_item not in inventory_item_defs:
                needed_items.append(default_item)

        self.steam.add_items(needed_items, steamid)

        response = make_response(needed_items); response.headers.set("Reponse-Type", "default_items"); return response

    def get_user_info(self, steamid: int):
        new_user = False

        user = self.db.users.find_one(
            {"steam_id": steamid}
        )

        # new user
        if user == None:

            new_user = True

            user = {
                "steam_id": steamid,
                "creation_date": int(time.time()),
                "is_banned": False,
                "elo": 500,
                "exp": 0
            }

            self.db.users.insert_one(
                user
            )

        response = make_response(
            {
                "banned": user["is_banned"],
                "creation_date": user["creation_date"],
                "elo": user["elo"],
                "exp": user["exp"],
                "user_id": str(user["steam_id"]),
                "new_user": new_user
            },
            200
        )

        response.headers["Response-Type"] = "get_user_info"

        return response
    
    def update_user_info(self, steamid: int):
        pass

    def get_wallpaper(self):
        wallpapers = os.listdir("/usr/local/share/scpbattlesapi/wallpapers")

        wallpaper_choice = random.choice(wallpapers)

        response = flask.send_file(f"/usr/local/share/scpbattlesapi/wallpapers/{wallpaper_choice}", mimetype='image/jpeg', as_attachment = True)

        response.headers["Response-Type"] = "wallpaper"

        return response

    def redeem_gift_card(self, code: str):
        steam_id = request.args.get("steam_id", type=int)

        card = self.db.itemgiftcards.find_one(
            {"code": code}
        )
        
        user = self.db.users.find_one(
            {"steam_id": steam_id}
        )

        if not user: 
            response = make_response("user not in database", 404); response.headers.set("Reponse-Type", "item-gift-card"); return response

        if not card:
            response = make_response("invalid item gift card code", 404); response.headers.set("Reponse-Type", "item-gift-card"); return response
        
        if card["used"]:
            response = make_response("code has already been used", 400); response.headers.set("Reponse-Type", "item-gift-card"); return response
        
        self.steam.add_items([card["itemdef"]], steam_id)

        self.db.itemgiftcards.find_one_and_update(
            {"code": code},
            {"$set": {"used": True}}
        )

        response = make_response(str(card["itemdef"]), 201); response.headers.set("Reponse-Type", "item-gift-card"); return response
        