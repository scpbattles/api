import time
import logging

import requests
import tomlkit
from flask import make_response, jsonify, request
from flask_restful import Resource

from scpbattlesapi.database import Database


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

                with open("/etc/scpbattlesapi/config.toml", "r") as file:
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