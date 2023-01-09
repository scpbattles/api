import json
import sys
import ssl
import socket
import os

from flask import Flask, request, jsonify, make_response, render_template
from flask_restful import Api, Resource

from address import Address
from generate_token import GenerateToken
from landing import LandingPage
from register_server import RegisterServer
from server_list import ServerList
from server import Server
from tos import TOS
from user_info import UserInfo
from validate_token import ValidateToken
from wallpaper import Wallpaper

if __name__ == "__main__":

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(UserInfo, "/users/<string:user_id>")
    api.add_resource(ServerList, "/servers")
    api.add_resource(Server, "/servers/<string:server_id>")
    api.add_resource(GenerateToken, "/generate_token")
    api.add_resource(ValidateToken, "/validate_token/<string:account_token>")
    api.add_resource(RegisterServer, "/register_server/<string:server_id>")
    api.add_resource(Address, "/ip")
    api.add_resource(TOS, "/tos")
    api.add_resource(LandingPage, "/")
    api.add_resource(Wallpaper, "/wallpaper.jpg")

    app.run(host="127.0.0.1", port=5000, debug=False)
