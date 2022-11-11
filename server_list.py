class ServerList(Resource):

    def get(self):

        with Database() as db:

            trim_servers()

            response = make_response(db.dict["online_servers"], 200)
            response.headers["Response-Type"] = "get_server_list"

            return response