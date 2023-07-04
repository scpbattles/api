import random
import os
import time

import flask
from flask import make_response, request, jsonify
from flask_restful import Resource
from requests import HTTPError

from models import DatabaseHandler, NotAUser

db = DatabaseHandler(database_path="test_database.yaml", config_path="test_config.yaml")

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

        if steam_id is None or key_item_id is None or case_item_id is None:
            response = make_response(
                "Missing query parameters", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response
        
        try:
            user = db.fetch_user(steam_id)

        except NotAUser:

            response = make_response(
                "Invalid steam id", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response

        inventory = user.inventory

        if key_item_id not in inventory:
            
            response = make_response(
                "Key not in inventory", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response
        
        if case_item_id not in inventory:

            response = make_response(
                "Case not in inventory", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response
        
        key = user.inventory[case_item_id]
        case = user.inventory[case_item_id]

        awarded_item, random_number = case.open(key)

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


class RegisterServer(Resource):
    # this needs to be finished!
    def put(self, server_id):
        
        # make sure server with this ID doesnt already exist
        try:
            server = db.fetch_server(
                server_id
            )

        except KeyError:
            pass 

        else:
            response = make_response(
                "Server name taken", 400
            )

            response.headers["Response-Type"] = "register_server"

            return response


    def delete(self, server_id):
        
        # this needs to be finished
        pass
    
class ServerList(Resource):

    def get(self):

        pass
    
class Server(Resource):
    def get(self, server_id):
        
        pass

    def put(self, server_id):

        pass

class UserInfo(Resource):

    def get(self, steamid):

        pass

    # Update user info, only official servers can do this
    def put(self, user_id):

        pass

class Wallpaper(Resource):
    def get(self):

        pass