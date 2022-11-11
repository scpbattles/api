class UserInfo(Resource):

    def get(self, user_id):
        with Database() as db:

            # Case insensitive
            user_id = user_id.lower()

            # If we can find the user, we return the data
            try:
                user_info = db.dict["user_info"][user_id]

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

        with Database() as db:

            user_id = user_id.lower()

            try:
                request_token = request.headers["auth_token"]
            except KeyError:
                response = make_response("did not supply auth token", 400)
                response.headers["Response-Type"] = "update_user_info"

                return response

            if request_token != db.dict["official_server_token"]:

                response = make_response("requires valid official token", 401)
                response.headers["Response-Type"] = "update_user_info"

                return response

            db.dict["user_info"][user_id].update(request.json)

            response = make_response("success", 201)
            response.headers["Response-Type"] = "update_user_info"

            return response