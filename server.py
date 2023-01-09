import time

from flask import make_response, jsonify, request
from flask_restful import Resource

from database import Database


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