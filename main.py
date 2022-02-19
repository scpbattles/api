from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import json
import string
import random
import collections
import time
import base64
import atexit

# List of potential characters for auth ids
id_characters = string.ascii_letters + string.ascii_uppercase

def flush(database):
    with open("database.json", "w") as file:
        json.dump(database,file, indent = 4, sort_keys = True)

def trim_servers():
    global db

    current_time = int(time.time())

    # We first trim off any servers that haven't pinged in over 10 seconds
    to_delete = []

    for server_id, last_ping in db["last_pinged"].items():
        print(last_ping)
        if current_time - last_ping > 10:
            to_delete.append(server_id)

    for server_id in to_delete:
        del db["online_servers"][server_id]
        del db["last_pinged"][server_id]

def official_server_authenticate(request):
    # First check if auth id was passed
    try:
        request_auth_id = request.headers["auth_id"]

    except:
        return "access denied", 401

    # Checks if auth id is valid
    if request_auth_id != official_server_auth_id:
        return "access denied", 401

    return True

# Create databse if it doesnt exist
try:
    with open("database.json", "r") as file:
        db = json.load(file)

except FileNotFoundError:
    input("CAN NOT FIND DATABASE! Press enter to generate a new one!")

    with open("default_db.json", "r") as file:
        db = json.load(file)

    with open("database.json", "w") as file:
        json.dump(db,file, indent = 4)

# Generate official server token
if db["official_server_token"] == None:
    print("UNABLE TO LOAD OFFICIAL SERVER AUTH TOKEN, GENERATING A NEW ONE")

    official_server_auth_token = ""

    for i in range(31):
        official_server_auth_token += random.choice(id_characters)

    db["official_server_token"] = official_server_auth_token

app = Flask(__name__)
api = Api(app)

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

        if request.json == None:
            response = make_response("no username/password supplied", 400)

            response.headers["Response-Type"] = "generate_token"

            print("NO USERNAME/PASSWORD SUPPLIED")

            return response

        username = request.json["username"]
        password = request.json["password"]

        if username not in db["account_passwords"]:

            response = make_response("account does not exist", 404)

            response.headers["Response-Type"] = "generate_token"

            return response

        actual_password = account_passwords[username]

        if password != actual_password:
            response = make_response("invalid password", 401)

            response.headers["Response-Type"] = "generate_token"

            print("INVALID PASSWORD")

            return response

        # If the username and password are correct, we return and store a temp token
        temp_token = ""

        for i in range(31):
            temp_token += random.choice(id_characters)

        # Remove all other bindings
        to_be_deleted = []

        for token, user in temp_account_tokens.items():
            if user == username:
                to_be_deleted.append(token)

        for token in to_be_deleted:
            del temp_account_tokens[token]

        # Eventually we will want these to expire
        temp_account_tokens[temp_token] = username

        print(temp_account_tokens)

        # Constructs response
        response = make_response(temp_token, 200)

        response.headers["Response-Type"] = "generate_token"

        print("SUCCESS")

        return response

class ValidateToken(Resource):
    global db

    def get(self, account_token):

        print(temp_account_tokens)

        try:
            validated_account_id = db["temp_account_tokens"][account_token]

        except KeyError:
            response = make_response("no account linked to token", 200)
            response.headers["Response-Type"] = "validate_token"

            return response

        # No longer valid
        del db["temp_account_tokens"][account_token]

        response = make_response(validated_account_id, 200)
        response.headers["Response-Type"] = "validate_token"

        return response

class UserInfo(Resource):

    def get(self, user_id):
        global db

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

        request_token = request.headers["auth_token"]

        if request_token != db["official_server_token"]:

            response = make_response("requires valid official token", 401)
            response.headers["Response-Type"] = "update_user_info"

            return response

        if user_name not in db["user_info"]:
            db["user_info"][user_name] = request.json

        else:
            user_data[user_name].update(request.json)

        response = make_response("success", 201)
        response.headers["Response-Type"] = "update_user_info"

        return response

class ServerList(Resource):

    def get(self):

        global db

        trim_servers()

        print(db["online_servers"])

        response = make_response(db["online_servers"], 200)
        response.headers["Response-Type"] = "get_server_list"

        return response

class Server(Resource):
    def get(self, server_id):

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

        global db

        if request.json == None:
            response = make_response("no server data provided", 400)
            response.headers["Response-Type"] = "update_server"

            return response

        print(request.headers)

        if "auth_token" not in request.headers:
            response = make_response("no auth token provided", 400)
            response.headers["Response-Type"] = "update_server"

            return response

        # Check if the server is in the dict now
        if server_id not in db["server_tokens"]:

            response = make_response("no such server", 404)
            response.headers["Response-Type"] = "update_server"

            return response

        if request.headers["auth_token"] != db["server_tokens"][server_id]:

            response = make_response("invalid server auth token", 401)
            response.headers["Response-Type"] = "update_server"

            return response

        # Updates server status
        if server_id not in db["online_servers"]:
            db["online_servers"][server_id] = request.json

        else:
            db["online_servers"][server_id].update(request.json)

        db["last_pinged"][server_id] = int(time.time())

        print(db["online_servers"])

        response = make_response("success", 200)
        response.headers["Response-Type"] = "update_server"

# class UserPets:
#     def
class Update(Resource):
    def get(self, update_id):

        return db["update"]


    def put(self, update_id):

        db["update"] = request.json

        return "successful", 201

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

api.add_resource(UserInfo,"/users/<string:user_name>")
api.add_resource(ServerList, "/servers")
api.add_resource(Server, "/servers/<string:server_id>")
api.add_resource(GenerateToken, "/generate_token")
api.add_resource(ValidateToken, "/validate_token/<string:account_token>")
api.add_resource(Update, "/updates/<string:update_id>")

if __name__ == "__main__":

    atexit.register(flush, db)

    app.run(host = "192.168.0.100", port = 80, debug = False)

    # from waitress import serve
    #
    # serve(app, host = "192.168.0.100", port = 80)
