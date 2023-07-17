import time
import os
import random

import flask
from flask import make_response, request, jsonify
from flask_restful import Resource

from scpbattlesapi.models import Key, InvalidKey
from scpbattlesapi.database import DatabaseHandler, NoMatchingUser, NoMatchingServer
from scpbattlesapi.steamapi import SteamAPI

db = DatabaseHandler(
    connection_string="localhost", 
    config_path="/etc/scpbattlesapi/config.yaml", 
    bad_words_path="/etc/scpbattlesapi/bad_words.json",
    steam_api=SteamAPI(os.environ.get("STEAM_API_KEY"))
)

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
            user = db.fetch_users(steam_id=steam_id)[0]

        except NoMatchingUser:

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
            server = db.fetch_servers(
                id=server_id
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
        
        try:
            online_servers = db.fetch_servers(
                # find any server that has pinged in the last 10 seconds
                last_pinged={"$gte": time.time() - 10}
            )
        except NoMatchingServer:
            online_servers = []

        servers_dict = {}

        # this is stupid but i need to do it for compatibility :(
        for server in online_servers:
            servers_dict[server.id] = {
                "name": server.id,
                "ip": server.ip,
                "port": server.port,
                "current_coalition": server.current_coalition,
                "current_foundation": server.current_foundation,
                "max_players": server.max_players,
                "official": server.is_official,
                "map": server.map,
                "mode": server.mode,
                "version": server.version,
                "current_players": server.current_players
            }

        response = make_response(
            servers_dict,
            200
        )

        response.headers["Response-Type"] = "get_server_list"

        return response

    
class Server(Resource):

    def put(self, server_id):

        auth_token = request.args.get("auth_token", type=str)
        official_server_token = request.args.get("official_auth_token", type=str)
        ip = request.args.get("steam_id", type=int)
        id = request.args.get("name", type=str)
        port = request.args.get("port", type=int)
        map = request.args.get("map", type=str)
        mode = request.args.get("mode", type=str)
        current_players = request.args.get("current_players", type=int)
        max_players = request.args.get("max_players", type=int)
        version = request.args.get("version", type=str)

        server = db.fetch_servers(
            id=server_id
        )[0]
        
        if server.token != auth_token:
            response = make_response("invalid server auth token", 401)
            response.headers["Response-Type"] = "update_server"

            return response


        if ip: server.ip = ip
        if port: server.port = port 
        if map: server.map = map
        if mode: server.mode = mode 
        if current_players: server.current_players = current_players
        if max_players: server.max_players = max_players
        if version: server.version = version

        server.last_pinged = time.time()

        server.save()

        response = make_response("success", 200)
        response.headers["Response-Type"] = "update_server"

        return response



class UserInfo(Resource):

    def get(self, steamid):

        user = db.fetch_users(
            steam_id=steamid
        )[0]

        response = make_response(
            {
                "banned": user.is_banned,
                "creation_date": user.creation_date,
                "elo": user.elo,
                "exp": user.exp,
                "user_id": steamid
            },
            200
        )

        response.headers["Response-Type"] = "get_user_info"

        return response

    # Update user info, only official servers can do this
    def put(self, user_id):

        pass

class Wallpaper(Resource):
    def get(self):

        wallpapers = os.listdir("/usr/local/share/scpbattlesapi/wallpapers")

        wallpaper_choice = random.choice(wallpapers)

        response = flask.send_file(f"/usr/local/share/scpbattlesapi/wallpapers/{wallpaper_choice}", mimetype='image/jpeg', as_attachment = True)

        response.headers["Response-Type"] = "wallpaper"

        return response