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

stripe.api_key = "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"
#stripe.api_key = "sk_test_51GGUk8DOZQ3m5pr7sgD0Vh7MzvNm5Q97BQGDB6Ur1Ge9fUeWmcCUUtNGxDrtX8AgMqyFyCc0BgyiSdFJszcnjJMc00VpfbnNTq"
#import PySimpleGUIWx as gui

geolocate_api_key = "b9df876be2834c1887e086d3d5fd8730"

smtp_api_key = "api-D11707DC552611ED92F1F23C91C88F4E"

# email
# default pet
# default available pets
# default elo
# date account created

default_user_info = {
    "allowed_pets": [0, 11],
    "elo": 500,
    "selected_pet": 0,
    "creation_date": None,
    "banned": False,
    "exp": 0,
    "allowed_skins": [100,200,300,400,500,600]
}

# List of potential characters for auth ids
id_characters = string.ascii_letters + string.ascii_uppercase

# Goes through active sessions and verifies payment, then adds respective items
def fufill_orders():

    global db

    while True:
        for user, checkouts in db["checkouts"].items():

            #print(f"{user} has {len(checkouts)} checkouts!")

            checkouts_to_delete = [] # We will remove session from this users list if they are expired or paid off

            for checkout in checkouts: # For each session the user has

                # Retrieve the session from stripe
                stripe_session = stripe.checkout.Session.retrieve(checkout["session_id"])

                if stripe_session["payment_status"] == "paid":
                    print(f"{user} has purchased {checkout['item']}!")

                    # If the item is a battle pass
                    if checkout["item"] == "battle_pass":
                        db["user_info"][user]["has_pass"] = True

                    # This is so janky and bad and stupid
                    elif checkout["item"].startswith("pet") == "pet":
                        db["user_info"][user]["allowed_pets"].append(checkout["item"].replace("pet", ""))

                    elif checkout["item"].startswith("skin"):
                        db["user_info"][user]["allowed_skins"].append(checkout["item"].replace("skin", ""))

                    checkouts_to_delete.append(checkout)

                    continue

                # Check if the session is expired
                if stripe_session["status"] == "expired":
                    checkouts_to_delete.append(checkout)
                    continue # Move onto the next session if this one is expired

            for checkout in checkouts_to_delete:
                checkouts.remove(checkout)

        time.sleep(10)
# Generates initial layout
# def generate_layout(data_form):
#     layout = []
#
#     if type(data_form) == dict:
#
#         for key, value in data_form.items():
#             row = []
#
#             # Add key
#             row.append(gui.Text(f"{key}: ", key = key))
#
#             # If the value contains a dictionary, we will have a seperate menu for that dict
#             # Different types of values will get different GUI elements for manipulating them
#             if type(value) is dict:
#                 row.append(gui.Button("Dict", key = f"-EDIT-{key}"))
#             elif type(value) is list:
#                 row.append(gui.Button("List", key = f"-EDIT-{key}"))
#             elif type(value) is bool:
#                 row.append(gui.Checkbox("", default=value, key = f"-UPDATE-{key}"))
#             elif type(value) is str or int: # Actual modifiable values
#                 row.append(gui.Input(value, do_not_clear = True, key = f"-UPDATE-{key}"))
#
#             layout.append(row)
#
#     elif type(data_form) == list:
#
#         print("Data form is list!")
#         for index, value in enumerate(data_form):
#
#             layout.append([gui.Text(f"{index}: "), gui.Input(default = value, do_not_clear = True, key = f"-UPDATE-{index}")])
#
#
#     layout.append([gui.Button("Submit", key = "-SUBMIT-"), gui.Stretch(), gui.Button("Home", key = "-HOME-")])
#
    # return layout

# Takes updated data from DB (data_form) and updates the GUI
def update_layout(window, data_form):

    # We treat different data forms differently

    if type(data_form) == dict:
        for key, value in data_form.items():
            # We only update values that can be modified

            if type(value) is str or int or bool:
                window[f"-UPDATE-{key}"].update(value)

    if type(data_form) == list:
        for index, value in enumerate(data_form):
            window[f"-UPDATE-{index}"].update(value)

def reload_db():
    global db

    while True:
        input("Press enter to reload DB...")

        with open("database.json","r") as file:
            db = json.load(file)

def flush(database):
    with open("database.json", "w") as file:
        json.dump(database,file, indent = 4, sort_keys = True)

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

class Wallpaper(Resource):
    def get(self):

        wallpapers = os.listdir("resources/wallpapers")

        wallpaper_choice = random.choice(wallpapers)

        response = flask.send_file(f"resources/wallpapers/{wallpaper_choice}", mimetype='image/jpeg', as_attachment = True)

        response.headers["Response-Type"] = "wallpaper"

        return response

class ResourcePack(Resource):
    def get(self):
        return flask.send_file("resources/downloads/paintingpack.zip", as_attachment=True)

class GenerateToken(Resource):

    # Users get temp tokens from the API
    # by sending their username and password

    # The user sends the token to the game server

    # The game server asks the API if the token
    # is tied to an account

    # The API responds with the account then
    # deletes the token

    def get(self):
        global db

        try:
            username = request.json["username"].lower()
            attempt_password = request.json["password"]

        except KeyError as e:

            print(dir(e))

            response = make_response("no username/password supplied", 400)

            response.headers["Response-Type"] = "generate_token"

            print("NO USERNAME/PASSWORD SUPPLIED")

            return response


        if username not in db["account_credentials"]:

            response = make_response("account does not exist", 404)

            response.headers["Response-Type"] = "generate_token"

            return response

        if db["user_info"][username]["banned"] == True:
            response = make_response("account banned", 403)

            response.headers["Response-Type"] = "generate_token"

            return response

        # Load salt
        salt = db["account_credentials"][username]["salt"]

        print(salt)

        attempt_password_hashed = hashlib.sha256(attempt_password.encode("utf-8") + salt.encode("utf-8")).hexdigest()
        actual_password_hashed = db["account_credentials"][username]["hashed_password"]

        if attempt_password_hashed != actual_password_hashed:
            response = make_response("invalid password", 401)

            response.headers["Response-Type"] = "generate_token"

            return response

        temp_token = secrets.token_urlsafe()

        # tokens expire after 30 minutes
        db["temp_account_tokens"][username] = {
            "token": temp_token,
            "expiration": time.time() + 1800
        }

        # send the token to the user
        response = make_response(temp_token, 200)
        response.headers["Response-Type"] = "generate_token"
        return response

class ValidateToken(Resource):
    global db

    def get(self, account_token):

        # the user that this token is bound to
        bound_user = None

        for user, token_data in db["temp_account_tokens"].items():
            if token_data["token"] == account_token:

                # get the user that this token is bound to
                bound_user = user

                # if the token is expired
                is_expired = token_data["expiration"] < time.time()

        if bound_user is None:
            response = make_response("no account linked to token", 404)
            response.headers["Response-Type"] = "validate_token"

            return response

        if is_expired:
            response = make_response("no account linked to token", 404)
            response.headers["Response-Type"] = "validate_token"

            return response

        response = make_response({"validated_token": account_token, "validated_user_id": bound_user}, 200)
        response.headers["Response-Type"] = "validate_token"

        return response

class UserInfo(Resource):

    def get(self, user_id):
        global db

        # Case insensitive
        user_id = user_id.lower()

        # If we can find the user, we return the data
        try:
            user_info = db["user_info"][user_id]

            response = make_response(jsonify(user_info), 200)
            response.headers["Response-Type"] = "get_user_info"

            return response

        except KeyError:
            # Otherwise, we return 404
            response = make_response("no user with that id", 404)

            response.headers["Response-Type"] = "get_user_info"

            return response

    # Update user info, only official servers can do this
    def put(self, user_id):
        global db

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

        flush(db)

        response = make_response("success", 201)
        response.headers["Response-Type"] = "update_user_info"

        return response

class ServerList(Resource):

    def get(self):

        global db

        trim_servers()

        response = make_response(db["online_servers"], 200)
        response.headers["Response-Type"] = "get_server_list"

        return response

class Server(Resource):
    def get(self, server_id):

        server_id = server_id.lower()


        global db

        trim_servers()

        try:
            server = db["online_servers"][server_id]

            response = make_response(jsonify(server), 200)
            response.headers["Response-Type"] = "get_server"

            return response

        except KeyError:
            response = make_response("server not online", 404)
            response.headers["Response-Type"] = "get_server"

            return response

    def put(self,server_id):

        server_id = server_id.lower()

        global db

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

class PetSelect(Resource): # Allows a user to change their selected pet
    def put(self, user_id):

        user_id = user_id.lower()
        # Log in
        username = request.json["username"].lower()
        password = request.json["password"]

        if username not in db["account_credentials"]:

            response = make_response("account does not exist", 404)

            response.headers["Response-Type"] = "pet_select"

            return response

        actual_password = db["account_credentials"][username]["password"]

        if password != actual_password:
            response = make_response("invalid password", 401)

            response.headers["Response-Type"] = "pet_select"

            return response

        # Try to change pet
        if "selected_pet" not in request.json:

            response = make_response("did not specify pet", 400)
            response.headers["Response-Type"] = "pet_select"

            return response

        selected_pet = request.json["selected_pet"]

        if selected_pet not in db["user_info"][user_id]["allowed_pets"]:

            response = make_response("you may not select that pet", 403)
            response.headers["Response-Type"] = "pet_select"

            return response

        if selected_pet not in db["possible_pets"]:
            response = make_response("not a possible pet", 400)
            response.headers["Response-Type"] = "pet_select"

            return response

        # If everything passes, we set the pet
        db["user_info"][user_id]["selected_pet"] = selected_pet

        response = make_response("success", 200)
        response.headers["Response-Type"] = "pet_select"

        return response

class ResetPassword(Resource):
    def post(self):

        email = request.json["email"]

        # the user id that is associated with this email
        user = None

        for user in db["account_credentials"].values():

            if email == user["email"]:

                # if there is an account with this email
                user = user

        if not user: # if we did not find a user

            # we dont tell the user if the email exists within the database
            return make_response("sent reset email if account exists", 200)

        reset_token = secrets.token_urlsafe()

        # attach a reset token to the associated user id
        db["reset_tokens"][user] = reset_token

        email_html = 
        email = {
            "api_key": smtp_api_key,
            'to': [f"SCP Battles Player <{email}>"],
            "sender": f"SCP Battles Support <help@voxany.net>",
            "subject": "Reset your password",
            "text_body": "Follow the link to reset your password",
            "html_body"
        }




class UpdateInfo(Resource):
    def get(self):
        return db["update_id"]

# class Update(Resource):
#     def get(self):
#
#         return flask.send_file("update/update.zip", as_attachment=True)
#
#     def put(self):
#         global db
#
#         print(request.json)
#
#         try:
#             auth_token = request.headers["auth_token"]
#         except:
#             response = make_response("did not send auth token", 400)
#
#             response.headers["Response-Type"] = "send_update"
#
#             return response
#
#         if auth_token != db["official_server_token"]:
#             response = make_response("invalid auth token", 401)
#
#             response.headers["Response-Type"] = "send_update"
#
#             return response
#
#         try:
#             update_link = request.json["discord_url"]
#             print(update_link)
#
#         except KeyError:
#             make_response("could not find discord url", 400)
#
#             response.headers["Response-Type"] = "send_update"
#
#             return response
#
#         response = requests.get(update_link)
#
#         open("update/update.zip", 'wb').write(response.content)
#
#         # Updates update ID
#         db["update_id"] += 1
#
#         response = make_response("success", 201)
#
#         response.headers["Response-Type"] = "send_update"
#
#         return response

class RegisterUser(Resource):
    def put(self):

        global db

        try:
            username = request.json["username"].lower()
            password = request.json["password"]
            email = request.json["email"]

        except KeyError:
            response = make_response("did not provide all required fields", 400)
            response.headers["Response-Type"] = "register"

            return response

        # Check if account already exists
        if username in db["account_credentials"]:
            response = make_response("account with that username already exists", 403)
            response.headers["Response-Type"] = "register"

            return response

        for field in (username,):
            if field.isalnum() != True:
                print(f"{field} is not alnum")
                response = make_response("username may only contain letters and numbers", 400)
                response.headers["Response-Type"] = "register"

                return response

        for bad_word in bad_words: # Check for vulgar language
            for field in (username,):
                if bad_word in field:
                    print(f"Found {bad_word} in field!")
                    response = make_response("one or more fields contained blocked keywords", 406)
                    response.headers["Response-Type"] = "register"

                    return response

        # Check if email taken
        for user in db["account_credentials"].values():
            if user["email"] == email:
                response = make_response("account with that email already exists", 403)
                response.headers["Response-Type"] = "register"

                return response

        # Generate salt
        salt = secrets.token_urlsafe()

        # Hash password
        hashed_password = hashlib.sha256(password.encode("utf-8") + salt.encode("utf-8")).hexdigest()

        credentials = {
            "salt": salt,
            "hashed_password": hashed_password,
            "email": email
        }

        # Adds credentials
        db["account_credentials"][username] = credentials

        # Adds default user info
        db["user_info"][username] = default_user_info

        # Adds creation date
        db["user_info"][username]["creation_date"] = time.time()

        db["user_info"][username]["user_id"] = username

        flush(db)

        response = make_response("success", 200)
        response.headers["Response-Type"] = "register"

        return response

        # user_name
        # PASSWORD
        # email
        # default pet
        # default available pets
        # default elo
        # date account created

class RegisterServer(Resource):
    def put(self, server_id):

        global db

        server_id = server_id.lower()

        # Look for official auth token
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

        flush(db)

        return response

    def delete(self, server_id):
        global db

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

class Address(Resource):

    def get(self):
        response = make_response(request.remote_addr, 200)
        response.headers["Response-Type"] = "get_ip"

        return response

class TOS(Resource):
    def get(self):

        with open("resources/html/tos.html") as file:
            data = file.read()

        response = make_response(data, 200)

        response.headers["Content-Type"] = "text/html; charset=utf-8"

        return response

class LandingPage(Resource):
    def get(self):

        with open("resources/html/landing.html") as file:
            data = file.read()

        response = make_response(data, 200)

        response.headers["Content-Type"] = "text/html; charset=utf-8"

        return response

class GenerateCheckout(Resource):
    def get(self, item):

        try:
            user_id = request.json["user_id"].lower()

        except KeyError as e:

            response = make_response("no user id provided", 400)
            response.headers["Response-Type"] = "generate_checkout"

            return response

        if user_id not in db["user_info"]: # User ID must exist in DB for item to be added
            response = make_response("no such user", 404)
            response.headers["Response-Type"] = "generate_checkout"

            return response

        if item not in db["items"]:
            response = make_response("not a possible item", 404)
            response.headers["Response-Type"] = "generate_checkout"

            return response

        item_data = db["items"][item]

        # Creates stripe session
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item_data["name"],
                            "description": item_data["description"],
                            "images": item_data["images"]
                        },

                        'unit_amount': item_data["cost"],
                    },

                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            cancel_url='https://www.youtube.com/watch?v=ArTJdcG-eRo',
        )

        # Create our own "checkout session"
        checkout = {
            "session_id": session.stripe_id,
            "item": item,
            "timestamp": time.time()
        }

        # Attaches session to user id
        if user_id not in db["checkouts"]:
            db["checkouts"][user_id] = []

        db["checkouts"][user_id].append(checkout) # Users can have multiple checkouts, so we use a list

        # Adds session to user's checkout history
        if user_id not in db["purchase_histories"]:
            db["purchase_histories"][user_id] = []

        db["purchase_histories"][user_id].append(checkout)

        response = make_response(session.url, 200)
        response.headers["Response-Type"] = "generate_checkout"

        return response

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
        print("Could not find bad words list")

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(UserInfo,"/users/<string:user_id>")
    api.add_resource(ServerList, "/servers")
    api.add_resource(Server, "/servers/<string:server_id>")
    api.add_resource(GenerateToken, "/generate_token")
    api.add_resource(ValidateToken, "/validate_token/<string:account_token>")
    api.add_resource(UpdateInfo, "/updateid")
    #api.add_resource(Update, "/update")
    api.add_resource(PetSelect, "/selectpet/<string:user_id>")
    api.add_resource(RegisterUser,"/register")
    api.add_resource(RegisterServer, "/register_server/<string:server_id>")
    api.add_resource(Address, "/ip")
    api.add_resource(TOS, "/tos")
    api.add_resource(LandingPage, "/")
    api.add_resource(GenerateCheckout,"/checkout/<string:item>")
    api.add_resource(ResourcePack, "/pack")
    api.add_resource(Wallpaper, "/wallpaper.jpg")

    # Creates DB window
    #gui.theme("Default1")

    # current_dict = db # We store the dict that the GUI is currently monitoring
    #
    # initial_layout = generate_layout(current_dict) # Start with initial dict
    #
    # window = gui.Window("DB", initial_layout)
    #
    # while True:
    #
    #     event, values = window.read(timeout = 100)
    #
    #     update_layout(window, current_dict) # Update with new values from db
    #
    #     #print(event)
    #     if event == None:
    #         sys.exit()
    #
    #     if event.startswith("-EDIT-"): # Changing dictionary
    #
    #         print("CHANGING")
    #         key_name = event.replace("-EDIT-","") # Extract keyname from event
    #
    #         current_dict = current_dict[key_name] # Change current dict to new one
    #
    #         new_layout = generate_layout(current_dict) # Regenerate layout for new dict
    #
    #         window.close() # Close old window
    #
    #         window = gui.Window("DB", new_layout)
    #
    #
    #     if event == "-SUBMIT-":
    #
    #         for element_key in values:
    #             dict_key = element_key.replace("-UPDATE-","") # Extract keyname from event
    #
    #             # Tries to convert input string to proper type (int, bool)
    #             try:
    #                 updated_value = type(current_dict[dict_key])(values[element_key])
    #
    #             except:
    #                 gui.popup(f"Unsupported data type for key {dict_key}\n\nMust be {type(current_dict[dict_key])}")
    #                 continue
    #
    #             if updated_value != current_dict[dict_key]:
    #                 print(f"detected change for {dict_key}")
    #
    #     if event == "-HOME-":
    #         current_dict = db
    #
    #         new_layout = generate_layout(current_dict) # Regenerate layout for new dict
    #
    #         window.close() # Close old window
    #
    #         window = gui.Window("DB", new_layout)

    #reload_thread = threading.Thread(target = reload_db)
    #reload_thread.start()

    atexit.register(flush, db)

    # Starts order fufillment thread
    fufillment_thread = threading.Thread(target = fufill_orders, daemon = True)
    fufillment_thread.start()

    # Loads cert
    context = ssl.SSLContext()
    context.load_cert_chain('certs/fullchain.pem', 'certs/privkey.pem')

    app.run(host=socket.gethostname(), port=443, ssl_context=context, debug=False)

    #app.run(host = "192.168.0.102", port = 443, debug = False)

    # from waitress import serve
    #
    # serve(app, host = "192.168.0.100", port = 80)
