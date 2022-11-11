class Server(Resource):
    def get(self, server_id):
        
        with Database() as db:
            server_id = server_id.lower()

            trim_servers()

            try:
                server = db.dict["online_servers"][server_id]

                response = make_response(jsonify(server), 200)
                response.headers["Response-Type"] = "get_server"

                return response

            except KeyError:
                response = make_response("server not online", 404)
                response.headers["Response-Type"] = "get_server"

                return response
    
    def put(self,server_id):

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


                if request.headers["official_server_token"] == db.dict["official_server_token"]:
                    request.json["official"] = True

                else:
                    request.json["official"] = False

            except KeyError:

                request.json["official"] = False

            if server_id not in db.dict["server_tokens"]:

                response = make_response("no such server", 404)
                response.headers["Response-Type"] = "update_server"

                return response

            if request.headers["auth_token"] != db["server_tokens"][server_id]["server_token"]:

                response = make_response("invalid server auth token", 401)
                response.headers["Response-Type"] = "update_server"

                return response

            # Updates server status
            if server_id not in db.dict["online_servers"]:
                db.dict["online_servers"][server_id] = request.json

            else:
                db.dict["online_servers"][server_id].update(request.json)

            db.dict["last_pinged"][server_id] = int(time.time())

            response = make_response("success", 200)
            response.headers["Response-Type"] = "update_server"

            return response