import os
import random

import flask
from flask_restful import Resource


class Wallpaper(Resource):
    def get(self):

        wallpapers = os.listdir("/usr/local/share/scpbattlesapi/wallpapers")

        wallpaper_choice = random.choice(wallpapers)

        response = flask.send_file(f"/usr/local/share/scpbattlesapi/wallpapers/{wallpaper_choice}", mimetype='image/jpeg', as_attachment = True)

        response.headers["Response-Type"] = "wallpaper"

        return response
