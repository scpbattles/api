import secrets
import hashlib
import time

from flask import request, make_response
from flask_restful import Resource

from database import Database


class GenerateToken(Resource):

    # Users get temp tokens from the API
    # by sending their username and password

    # The user sends the token to the game server

    # The game server asks the API if the token
    # is tied to an account

    # The API responds with the account then
    # deletes the token

    def get(self): 

        with Database() as db:

            try:
                username = request.json["username"].lower()
                attempt_password = request.json["password"]

            except KeyError as e:

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

            # if attempt_password_hashed != actual_password_hashed:
            #     response = make_response("invalid password", 401)
            #
            #     response.headers["Response-Type"] = "generate_token"
            #
            #     return response

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
