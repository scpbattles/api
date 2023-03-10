import random
import os
import time

import flask
from flask import make_response, request, jsonify
from flask_restful import Resource
from requests import HTTPError

from databasehandler import DatabaseHandler, NotAUser

database = DatabaseHandler(database_path="")

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
            user = database.fetch_user(steam_id)

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
        
        case = database.

class RegisterServer(Resource):
    def put(self, server_id):
        
        pass

    def delete(self, server_id):
        
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