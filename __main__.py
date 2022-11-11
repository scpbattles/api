import json
import string
import random
import collections
import time
import base64
import atexit
import hashlib
import threading
import sys
import ssl
import socket
import os
import random

import flask
from flask import Flask, request, jsonify, make_response, render_template
from flask_restful import Api, Resource
import stripe
import requests
import secrets

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

default_user_info = {
    "allowed_pets": [0, 11],
    "elo": 500,
    "selected_pet": 0,
    "creation_date": None,
    "banned": False,
    "exp": 0,
    "allowed_skins": [100,200,300,400,500,600]
}

def trim_servers():
    global db

    current_time = int(time.time())

    # We first trim off any servers that haven't pinged in over 10 seconds
    to_delete = []

    for server_id, last_ping in db["last_pinged"].items():
        if current_time - last_ping > 10:
            to_delete.append(server_id)

    for server_id in to_delete:
        del db["online_servers"][server_id]
        del db["last_pinged"][server_id]

if __name__ == "__main__":

    # Create database if it doesnt exist
    try:
        with open("database.json", "r") as file:
            db = json.load(file)

    except FileNotFoundError:
        input("CAN NOT FIND DATABASE! Press enter to generate a new one!")

        with open("default_db.json", "r") as file:
            db = json.load(file)

        with open("database.json", "w") as file:
            json.dump(db, file, indent=4)

    # Generate official server token
    if db["official_server_token"] == None:
        print("UNABLE TO LOAD OFFICIAL SERVER AUTH TOKEN, GENERATING A NEW ONE")

        db["official_server_token"] = secrets.token_urlsafe()

    try:
        with open("resources/bad_words.json", "r") as file:
            bad_words = json.load(file)
    except FileNotFoundError:
        print("could not find bad words list")

        sys.exit()

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(UserInfo,"/users/<string:user_id>")
    api.add_resource(ServerList, "/servers")
    api.add_resource(Server, "/servers/<string:server_id>")
    api.add_resource(GenerateToken, "/generate_token")
    api.add_resource(ValidateToken, "/validate_token/<string:account_token>")
    api.add_resource(RegisterServer, "/register_server/<string:server_id>")
    api.add_resource(Address, "/ip")
    api.add_resource(TOS, "/tos")
    api.add_resource(LandingPage, "/")
    api.add_resource(Wallpaper, "/wallpaper.jpg")
    atexit.register(flush, db)

    # Starts order fufillment thread
    fufillment_thread = threading.Thread(target = fufill_orders, daemon = True)
    fufillment_thread.start()

    # Loads cert
    context = ssl.SSLContext()
    context.load_cert_chain('certs/fullchain.pem', 'certs/privkey.pem')

    app.run(host=socket.gethostname(), port=443, ssl_context=context, debug=False)
