from flask import Flask
from flask_restful import Api

from scpbattlesapi.views import UserInfo, ServerList, Server, RegisterServer, Address, Wallpaper, Case

app = Flask(__name__)
api = Api(app)

api.add_resource(UserInfo, "/users/<string:steamid>")
api.add_resource(ServerList, "/servers")
api.add_resource(Server, "/servers/<string:server_id>")
api.add_resource(RegisterServer, "/register_server/<string:server_id>")
api.add_resource(Address, "/ip")
api.add_resource(Wallpaper, "/wallpaper.jpg")
api.add_resource(Case, "/case")