from flask import Flask, request, jsonify, make_response, render_template
from flask_restful import Api, Resource

from views import UserInfo, ServerList, Server, RegisterServer, Address, Wallpaper, Case

if __name__ == "__main__":

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(UserInfo, "/users/<string:steamid>")
    api.add_resource(ServerList, "/servers")
    api.add_resource(Server, "/servers/<string:server_id>")
    api.add_resource(RegisterServer, "/register_server/<string:server_id>")
    api.add_resource(Address, "/ip")
    #api.add_resource(TOS, "/tos")
    api.add_resource(Wallpaper, "/wallpaper.jpg")
    api.add_resource(Case, "/case")

    app.run(host="127.0.0.1", port=5000, debug=False)
