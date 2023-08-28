from flask import Flask

from scpbattlesapi.scpbattlesapi import SCPBattlesAPI

app = Flask(__name__)

api = SCPBattlesAPI()

app.add_url_rule("/case", view_func=api.unbox, methods=["POST"])
app.add_url_rule("/users/<int:steamid>", view_func=api.get_user_info, methods=["GET"])
app.add_url_rule("/users/<int:steamid>", view_func=api.update_user_info, methods=["PUT"])
app.add_url_rule("/crafting", view_func=api.craft, methods=["POST"])
app.add_url_rule("/register_server/<string:server_id>", view_func=api.register_sever, methods=["POST"])
app.add_url_rule("/register_server/<string:server_id>", view_func=api.delete_server, methods=["DELETE"])
app.add_url_rule("/servers", view_func=api.get_online_servers, methods=["GET"])
app.add_url_rule("/servers/<string:server_id>", view_func=api.update_server_listing, methods=["PUT"])
app.add_url_rule("/defaultitems/<int:steamid>", view_func=api.give_default_items, methods=["POST"])
app.add_url_rule("/wallpaper.jpg", view_func=api.get_wallpaper, methods=["GET"])
app.add_url_rule("/itemgiftcard/<string:code>", view_func=api.redeem_gift_card, methods=["POST"])