import json
import sys
import ssl
import socket
import os

from flask import Flask, request, jsonify, make_response, render_template
from flask_restful import Api, Resource

from scpbattlesapi.address import Address
from scpbattlesapi.generate_token import GenerateToken
from scpbattlesapi.landing import LandingPage
from scpbattlesapi.register_server import RegisterServer
from scpbattlesapi.server_list import ServerList
from scpbattlesapi.server import Server
from scpbattlesapi.tos import TOS
from scpbattlesapi.user_info import UserInfo
from scpbattlesapi.validate_token import ValidateToken
from scpbattlesapi.wallpaper import Wallpaper

if __name__ == "__main__":

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(UserInfo, "/users/<string:steamid>")
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
