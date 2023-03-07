import logging
import random
import secrets 
import time 
import json
import os

import flask
from flask import make_response, request, jsonify
from flask_restful import Resource
import requests
from requests import HTTPError
import yaml

from steamapi import get_inventory, add_item, consume_item
from database import Database
from config import Config



class Address(Resource):

    def get(self):
        response = make_response(request.remote_addr, 200)
        response.headers["Response-Type"] = "get_ip"

        return response

class Case(Resource):

    def post(self):
        
        with Config() as config:
            steam_api_key = config["steam_api_key"]
            case_probabilities = config["case_probabilities"]
        
        steam_id = request.args.get("steam_id", type=int)
        key_item_id = request.args.get("key_item_id", type=int)
        case_item_id = request.args.get("case_item_id", type=int)

        if steam_id is None:
            return "Missing steam_id query parameter", 400
        if key_item_id is None:
            return "Missing key_item_id query parameter", 400
        if case_item_id is None:
            return "Missing case_item_id query parameter", 400

        try:
            inventory = get_inventory(steam_id, steam_api_key)
            
        except HTTPError:
            return "Failed to fetch inventory", 500

        key_item_data = None
        case_item_data = None

        for item in inventory:
            logging.warning(item)

        # look for the key item in the inventory and check if it is a key        
        for item in inventory:

            #logging.warning(item)

            if item["itemid"] != key_item_id:
                continue
            
            if item["itemdefid"] not in config["key_case_map"]:
                return "Specified key is not a key", 400
            
            key_item_data = item
        
        if key_item_data is None:
            return "Specified key not in inventory", 400
        
        # look for case item in the inventory and check if its a case and matches the key type
        for item in inventory:

            if item["itemid"] != case_item_id:
                continue 
            
            # check if case exists in list of cases that the specified key can open
            if item["itemdefid"] not in config["key_case_map"][key_item_data["itemdefid"]]:
                return "Specified case does not match specified key", 400

            case_item_data = item
        
        if case_item_data is None:
            return "Specified case not in inventory", 400

        random_number = random.randint(1, 10000)

        logging.warning(f"Random number :{random_number}")

        # get probabilities for this case
        item_group_probabilities = case_probabilities[case_item_data["itemdefid"]]

        logging.warning(f"Item group probs:{item_group_probabilities}")

        # random number height is the highest the random number can be to get those items
        for random_number_height in item_group_probabilities.keys():

            logging.warning(f"Random number height :{random_number_height}")
            logging.warning(f"Random number height type :{type(random_number)}")
            
            # if our random number is lower than this item group's number height, we stop
            if random_number <= random_number_height:
                possible_items = case_probabilities[case_item_data["itemdefid"]][random_number_height]

                break
            
            # if it was higher we go to the next number height
            else:
                continue 
        
        awarded_item = random.choice(possible_items)

        try:
            # consume key
            consume_item(
                item_id=key_item_data["itemid"],
                steam_id=steam_id,
                steam_api_key=steam_api_key
            )
        
        except HTTPError:
            return "Failed to consume key item", 500
        
        try: 
            # consume case
            consume_item(
                item_id=case_item_data["itemid"],
                steam_id=steam_id,
                steam_api_key=steam_api_key
            )
        
        except HTTPError:
            return "Failed to consume case item", 500

        try:
            # give awarded item
            add_item(
                item_def=awarded_item,
                steam_id=steam_id,
                steam_api_key=steam_api_key
            )
        
        except HTTPError:
            return "Failed to give award item", 500

        response = make_response(
            jsonify(
                {
                    "awarded_item": awarded_item,
                    "random_number": random_number
                }
            )
        )
        response.headers["Response-Type"] = "open_case"

        return response

class GenerateToken(Resource):

    # Users get temp tokens from the API
    # by sending their username and password

    # The user sends the token to the game server

    # The game server asks the API if the token
    # is tied to an account

    # The API responds with the account then
    # deletes the token

    def get(self): 

        with Database() as db:

            try:
                username = request.json["username"].lower()
                # attempt_password = request.json["password"]

            except KeyError as e:

                response = make_response("no username/password supplied", 400)

                response.headers["Response-Type"] = "generate_token"

                #print("NO USERNAME/PASSWORD SUPPLIED")

                return response


            if username not in db["account_credentials"]:

                response = make_response("account does not exist", 404)

                response.headers["Response-Type"] = "generate_token"

                return response

            if db["user_info"][username]["banned"] == True:
                response = make_response("account banned", 403)

                response.headers["Response-Type"] = "generate_token"

                return response

            # Load salt
            salt = db["account_credentials"][username]["salt"]

            #print(salt)

            # attempt_password_hashed = hashlib.sha256(attempt_password.encode("utf-8") + salt.encode("utf-8")).hexdigest()
            # actual_password_hashed = db["account_credentials"][username]["hashed_password"]

            # if attempt_password_hashed != actual_password_hashed:
            #     response = make_response("invalid password", 401)
            #
            #     response.headers["Response-Type"] = "generate_token"
            #
            #     return response

            temp_token = secrets.token_urlsafe()

            # tokens expire after 30 minutes
            db["temp_account_tokens"][username] = {
                "token": temp_token,
                "expiration": time.time() + 1800
            }

            # send the token to the user
            response = make_response(temp_token, 200)
            response.headers["Response-Type"] = "generate_token"
            return response
        
class LandingPage(Resource):

    def get(self):

        with open("resources/html/landing.html") as file:
            data = file.read()

        response = make_response(data, 200)

        response.headers["Content-Type"] = "text/html; charset=utf-8"

        return response

class RegisterServer(Resource):
    def put(self, server_id):

        with Database() as db:

            with open("/etc/scpbattlesapi/bad_words.json", "r") as file:
                bad_words = json.load(file)

            server_id = server_id.lower()

            # look for official auth token
            try:
                auth_token = request.headers["auth_token"]

            except KeyError:
                response = make_response("no auth token provided", 400)
                response.headers["Response-Type"] = "update_server"

                return response

            # Look for discord id
            try:
                discord_id = request.json["discord_id"]

            except KeyError:
                response = make_response("no discord id provided", 400)
                response.headers["Response-Type"] = "update_server"

                return response

            # Ensure official server token matches
            if auth_token != db["official_server_token"]:
                response = make_response("invalid token", 401)
                response.headers["Response-Type"] = "register_server"

                return response

            # Check if that server id is taken
            if server_id in db["server_tokens"]:
                response = make_response("server with that id already exists", 403)
                response.headers["Response-Type"] = "register_server"

                return response

            # Ensure all text is alphanumeric
            for field in (server_id,):
                if field.isalnum() != True:
                    response = make_response("one or more fields contained non-ascii characters", 400)
                    response.headers["Response-Type"] = "register"

                    return response

            for bad_word in bad_words: # Check for vulgar language
                for field in (server_id,):
                    if field in bad_word:
                        response = make_response("one or more fields contained blocked keywords", 406)
                        response.headers["Response-Type"] = "register"

                        return response

            server_token = secrets.token_urlsafe()

            db["server_tokens"][server_id] = {"server_token": server_token, "discord_id": discord_id}

            response = make_response(server_token, 201)

            response.headers["Response-Type"] = "register_server"

            return response

    def delete(self, server_id):
        
        with Database() as db:

            server_id = server_id.lower()

            try:
                discord_id = request.json["discord_id"]
            except KeyError:
                response = make_response("no discord id provided", 400)

                response.headers["Response-Type"] = "delete_server"

                return response

            if server_id not in db["server_tokens"]:
                response = make_response("no such server", 404)

                response.headers["Response-Type"] = "delete_server"

                return response


            if discord_id != db["server_tokens"][server_id]["discord_id"]:
                response = make_response("invalid discord id", 401)

                response.headers["Response-Type"] = "delete_server"

                return response


            del db["server_tokens"][server_id]

            response = make_response("server deleted", 201)

            response.headers["Response-Type"] = "delete_server"

            return response
    
class ServerList(Resource):

    def get(self):

        with Database() as db:

            # use this time to compare to when the server last pinged
            current_time = int(time.time())

            # We first trim off any servers that haven't pinged in over 10 seconds
            to_delete = []

            # go through every server
            for server_id, last_ping in db["last_pinged"].items():
                if current_time - last_ping > 10:
                    to_delete.append(server_id)

            # delete every server that hasnt pinged in the last 10 seconds
            for server_id in to_delete:
                del db["online_servers"][server_id]
                del db["last_pinged"][server_id]

            # return a dict of online servers
            response = make_response(db["online_servers"], 200)
            response.headers["Response-Type"] = "get_server_list"

            return response
    
class Server(Resource):
    def get(self, server_id):

        with Database() as db:

            # lowercase server_id
            server_id = server_id.lower()

            # use this time to compare to when they last pinged
            current_time = int(time.time())

            # We first trim off any servers that haven't pinged in over 10 seconds
            to_delete = []

            # go through every server
            for server_id, last_ping in db["last_pinged"].items():
                if current_time - last_ping > 10:
                    to_delete.append(server_id)

            # delete every server that hasnt pinged in the last 10 seconds
            for server_id in to_delete:
                del db["online_servers"][server_id]
                del db["last_pinged"][server_id]

            # look for the requested server in the online servers list
            try:
                server = db["online_servers"][server_id]

                # send the server data
                response = make_response(jsonify(server), 200)
                response.headers["Response-Type"] = "get_server"

                return response

            # if the server is not in the list, we return 404
            except KeyError:
                response = make_response("server not online", 404)
                response.headers["Response-Type"] = "get_server"

                return response

    def put(self, server_id):

        with Database() as db:

            server_id = server_id.lower()

            try:
                request.headers["auth_token"]

            except KeyError:
                response = make_response("no auth token provided", 400)
                response.headers["Response-Type"] = "update_server"

                print(request.headers)

                print(list(request.headers))
                
                return response

            try:
                request.headers["official_server_token"]

                if request.headers["official_server_token"] == db["official_server_token"]:
                    request.json["official"] = True

                else:
                    request.json["official"] = False

            except KeyError:

                request.json["official"] = False

            if server_id not in db["server_tokens"]:

                response = make_response("no such server", 404)
                response.headers["Response-Type"] = "update_server"

                return response

            if request.headers["auth_token"] != db["server_tokens"][server_id]["server_token"]:

                response = make_response("invalid server auth token", 401)
                response.headers["Response-Type"] = "update_server"

                return response

            # Updates server status
            if server_id not in db["online_servers"]:
                db["online_servers"][server_id] = request.json

            else:
                db["online_servers"][server_id].update(request.json)

            db["last_pinged"][server_id] = int(time.time())

            response = make_response("success", 200)
            response.headers["Response-Type"] = "update_server"

            return response

class TOS(Resource):
    def get(self):
        
        with open("resources/html/tos.html") as file:
            data = file.read()

        response = make_response(data, 200)

        response.headers["Content-Type"] = "text/html; charset=utf-8"

        return response

class UserInfo(Resource):

    def get(self, steamid):
        with Database() as db:

            # Case insensitive
            steamid = steamid.lower()

            # If we can find the user, we return the data
            try:
                user_info = db["user_info"][steamid]

                response = make_response(jsonify(user_info), 200)
                response.headers["Response-Type"] = "get_user_info"

                return response

            except KeyError:
                # if we do not have user info for this steamID yet, we make an entry for them and give them the default items
                
                print(f"New user {steamid}")

                with open("/etc/scpbattlesapi/config.yaml", "r") as file:
                    config = yaml.safe_load(file.read())

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

                resp = requests.post("http://api.steampowered.com/IInventoryService/AddItem/v1", params=params, headers=headers, data=data)

                logging.warning(resp.status_code)
                logging.warning(resp.raw)

                print(resp.status_code)

                print(resp.raw)

                # create default user info
                db["user_info"][steamid] = {
                    "banned": False,
                    "creation_date": time.time(),
                    "elo": 500,
                    "exp": 0,
                    "user_id": steamid
                }

                # get info to be returned to client
                user_info = db["user_info"][steamid]

                response = make_response(jsonify(user_info), 201)
                response.headers["Response-Type"] = "get_user_info"

                return response

    # Update user info, only official servers can do this
    def put(self, user_id):

        with Database() as db:

            user_id = user_id.lower()

            try:
                request_token = request.headers["auth_token"]
            except KeyError:
                response = make_response("did not supply auth token", 400)
                response.headers["Response-Type"] = "update_user_info"

                return response

            if request_token != db["official_server_token"]:

                response = make_response("requires valid official token", 401)
                response.headers["Response-Type"] = "update_user_info"

                return response

            db["user_info"][user_id].update(request.json)

            response = make_response("success", 201)
            response.headers["Response-Type"] = "update_user_info"

            return response

class ValidateToken(Resource):

    def get(self, account_token):
        
        with Database() as db:
            # the user that this token is bound to
            bound_user = None

            for user, token_data in db["temp_account_tokens"].items():
                if token_data["token"] == account_token:

                    # get the user that this token is bound to
                    bound_user = user

                    # if the token is expired
                    is_expired = token_data["expiration"] < time.time()

            if bound_user is None:
                response = make_response("no account linked to token", 404)
                response.headers["Response-Type"] = "validate_token"

                return response

            if is_expired:
                response = make_response("no account linked to token", 404)
                response.headers["Response-Type"] = "validate_token"

                return response

            response = make_response({"validated_token": account_token, "validated_user_id": bound_user}, 200)
            response.headers["Response-Type"] = "validate_token"

            return response

class Wallpaper(Resource):
    def get(self):

        wallpapers = os.listdir("/usr/local/share/scpbattlesapi/wallpapers")

        wallpaper_choice = random.choice(wallpapers)

        response = flask.send_file(f"/usr/local/share/scpbattlesapi/wallpapers/{wallpaper_choice}", mimetype='image/jpeg', as_attachment = True)

        response.headers["Response-Type"] = "wallpaper"

        return response