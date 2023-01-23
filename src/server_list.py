import time

from flask import make_response
from flask_restful import Resource

from database import Database


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