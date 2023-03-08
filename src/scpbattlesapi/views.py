import random
import os

import flask
from flask import make_response, request, jsonify
from flask_restful import Resource
from requests import HTTPError

from database import Database
from config import Config
import models

api = models.SCPBattlesAPI(database_path="test_database.yaml", config_path="test_config.yaml")

class Address(Resource):

    def get(self):
        response = make_response(request.remote_addr, 200)
        response.headers["Response-Type"] = "get_ip"
        
        return response

class Case(Resource):

    def post(self):

        steam_id = request.args.get("steam_id", type=int)
        key_item_id = request.args.get("key_item_id", type=int)
        case_item_id = request.args.get("case_item_id", type=int)

        if steam_id is None:
            return "Missing steam_id query parameter", 400
        if key_item_id is None:
            return "Missing key_item_id query parameter", 400
        if case_item_id is None:
            return "Missing case_item_id query parameter", 400
        
        user = api.fetch_user(steam_id)


        
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

            response = make_response(server_token, 201)

            response.headers["Response-Type"] = "register_server"

            return response

    def delete(self, server_id):
        

            response = make_response("server deleted", 201)

            response.headers["Response-Type"] = "delete_server"

            return response
    
class ServerList(Resource):

    def get(self):

            # return a dict of online servers
            response = make_response(db["online_servers"], 200)
            response.headers["Response-Type"] = "get_server_list"

            return response
    
class Server(Resource):
    def get(self, server_id):

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

        response = make_response(jsonify(user_info), 201)
        response.headers["Response-Type"] = "get_user_info"

        return response

    # Update user info, only official servers can do this
    def put(self, user_id):


        response = make_response("success", 201)
        response.headers["Response-Type"] = "update_user_info"

        return response

class ValidateToken(Resource):

    def get(self, account_token):
        

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