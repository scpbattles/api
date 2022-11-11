import random

class Wallpaper(Resource):
    def get(self):

        wallpapers = os.listdir("resources/wallpapers")

        wallpaper_choice = random.choice(wallpapers)

        response = flask.send_file(f"resources/wallpapers/{wallpaper_choice}", mimetype='image/jpeg', as_attachment = True)

        response.headers["Response-Type"] = "wallpaper"

        return response
