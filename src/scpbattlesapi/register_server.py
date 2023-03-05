import secrets
import json

from flask import request, make_response
from flask_restful import Resource

from scpbattlesapi.database import Database

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