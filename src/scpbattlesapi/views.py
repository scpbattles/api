import random
import os
import time

import flask
from flask import make_response, request, jsonify
from flask_restful import Resource
from requests import HTTPError

from models import Key, InvalidKey
from database import DatabaseHandler, NotAUser

db = DatabaseHandler(connection_string="test_database.yaml", config_path="test_config.yaml")

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
                "missing query parameters", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response
        
        try:
            user = db.fetch_user(steam_id)

        except NotAUser:

            response = make_response(
                "user not in database", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response

        if key_item_id not in user.inventory:
            
            response = make_response(
                "key not in inventory", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response
        
        if case_item_id not in user.inventory:

            response = make_response(
                "case not in inventory", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response
        
        key = user.inventory[case_item_id]
        case = user.inventory[case_item_id]

        if type(case) is not Case:

            response = make_response(
                "specified case is not a case", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response

        try:
            awarded_item, random_number = case.open(key)

        except InvalidKey:

            response = make_response(
                "key incompatible with case type", 400
            )

            response.headers["Response-Type"] = "open_case"

            return response

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