from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import json
import string
import random
import collections
import time
import base64

# List of potential characters for auth ids
id_characters = string.ascii_letters + string.ascii_uppercase

def trim_servers():
    global last_pinged
    global online_servers

    current_time = int(time.time())

    # We first trim off any servers that haven't pinged in over 10 seconds
    to_delete = []

    for server_id, last_ping in last_pinged.items():
        print(last_ping)
        if current_time - last_ping > 10:
            to_delete.append(server_id)

    for server_id in to_delete:
        del online_servers[server_id]
        del last_pinged[server_id]

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

try:
    with open("database.json", "r") as file:
        db = json.load(file)

except FileNotFoundError:
    input("CAN NOT FIND DATABASE! Press enter to generate a new one!")

    db = {
        "account_passwords": {
            "users"
        }
    }
try:
    with open("update.json", "r") as file:
        update = json.load(file)

except FileNotFoundError:
    print("Could not find update")

    update = {}

    with open("update.json", "w") as file:
        json.dump(update, file)

# Generates or loads account passwords
try:
    with open("account_passwords.json", "r") as file:
        account_passwords = json.load(file)

except FileNotFoundError:
    print("COULD NOT FIND ACCOUNT PASSSWORDS, GENERATING A NEW FILE")

    account_passwords = {}

    with open("account_passwords.json", "w") as file:
        json.dump(account_passwords, file)



# Generates or loads auth id
try:
    with open("official_server_auth_id.txt", "r") as file:
        official_server_auth_id = file.read()

except FileNotFoundError:
    print("UNABLE TO LOAD OFFICIAL SERVER AUTH ID, GENERATING A NEW ONE")

    official_server_auth_id = ""

    for i in range(31):
        official_server_auth_id += random.choice(id_characters)

    with open("official_server_auth_id.txt", "w") as file:
        file.write(official_server_auth_id)


# Loads existing user data
try:
    with open("user_data.json", "r") as file:
        user_data = json.load(file)
except FileNotFoundError:
    user_data = {
        "sample_user": {
            "elo": "123",
            "banned": False,
            "agreed_toc": True,
            "over_13": True
        }
    }

    with open("user_data.json", "w") as file:
        json.dump(user_data, file)

# Loads servers auth ids
try:
    with open("server_auths.json", "r") as file:
        server_auths = json.load(file)

except FileNotFoundError:
    server_auths = {}

    with open("server_auths.json", "w") as file:
        json.dump(server_auths,file)

# Records the last time a server updated their info (meaning they are online)
last_pinged = {}

# List of all online servers
online_servers = {}

# Dict of users and their temp tokens
temp_account_tokens = {}

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
            response = make_response(jsonify("no username/password supplied"), 400)

            response.headers["Response-Type"] = "generate_token"

            print("NO USERNAME/PASSWORD SUPPLIED")

            return response

        username = request.json["username"]
        password = request.json["password"]

        if username not in db["account_passwords"]:
            with open("account_passwords.json", "r") as file:
                account_passwords = json.load(file)

            # Check if the server is in the dict now
            if username not in account_passwords:
                response = make_response(jsonify("account does not exist"), 404)

                response.headers["Response-Type"] = "generate_token"

                return response

        actual_password = account_passwords[username]

        if password != actual_password:
            response = make_response(jsonify("invalid password"), 401)

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
        response = make_response(jsonify(temp_token), 200)

        response.headers["Response-Type"] = "generate_token"

        print("SUCCESS")

        return response

class ValidateToken(Resource):
    global temp_account_tokens

    def get(self, account_token):

        print(temp_account_tokens)

        try:
            validated_account_id = temp_account_tokens[account_token]

        except KeyError:
            #raise
            return "no account linked to token", 404

        # No longer valid
        del temp_account_tokens[account_token]

        return validated_account_id, 200

class User(Resource):

    def get(self, user_name):

        # If we can find the user, we return the data
        if user_name in user_data:
            # Constructs response
            response = make_response(jsonify(user_data[user_name]), 200)

            response.headers["Response-Type"] = "get_user_info"

            return response

        # Otherwise, we return 404
        else:
            response = make_response(jsonify("no user"), 404)

            response.headers["Response-Type"] = "generate_token"

            return response

    # Update user info, only official servers can do this
    def put(self, user_name):

        # Authenticates request
        auth_result = official_server_authenticate(request)

        if auth_result != True: # If it doesn't pass authentication, we return an "unauthorized" response
            response = make_response(jsonify(auth_result), 400)

            response.headers["Response-Type"] = "update_user_info"

            return response

        user_data[user_name].update(request.json)

        # Saves new data to file
        with open("data.json", "w") as file:
            json.dump(user_data, file, indent = 4, sort_keys= True)

        response = make_response(jsonify("success"), 400)

        response.headers["Response-Type"] = "update_user_info"
        return "success", 201

class ServerList(Resource):

    def get(self):

        trim_servers(servers)

        return online_servers

class Server(Resource):
    def get(self, server_id):

        trim_servers()

        if server_id not in online_servers:
            return "server not online", 404

        return online_servers[server_id]

    def put(self,server_id):

        global server_auths

        if request.json == None:
            return "no server data provided", 400

        print(request.headers)

        if "auth_id" not in request.headers:
            return "no auth_id provided", 400

        # If we cant find the server in the id's dict, we reload the id file
        if server_id not in server_auths:
            with open("server_auths.json", "r") as file:
                server_auths = json.load(file)

            # Check if the server is in the dict now
            if server_id not in server_auths:
                return "server not in auth database", 404

        if request.headers["auth_id"] != server_auths[server_id]:
            return "invalid server auth id", 401

        # Updates server status
        if server_id not in online_servers:
            online_servers[server_id] = request.json

        else:
            online_servers[server_id].update(request.json)

        last_pinged[server_id] = int(time.time())

        print(online_servers)

        return "success", 201

class Update(Resource):
    def get(self, update_id):

        return update


    def put(self, update_id):

        global update

        update = request.json

        with open("update.json", "w") as file:
            json.dump(update, file, indent = 4)

        return "successful", 201



# class UpdateList(Resource):
#     get ():

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

api.add_resource(User,"/users/<string:user_name>")
api.add_resource(ServerList, "/servers")
api.add_resource(Server, "/servers/<string:server_id>")
api.add_resource(GenerateToken, "/generate_token")
api.add_resource(ValidateToken, "/validate_token/<string:account_token>")
api.add_resource(Update, "/updates/<string:update_id>")

if __name__ == "__main__":
    app.run(host = "192.168.0.100", port = 80, debug = False)

    # from waitress import serve
    #
    # serve(app, host = "192.168.0.100", port = 80)
