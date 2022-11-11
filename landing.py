class LandingPage(Resource):
    def get(self):

        with open("resources/html/landing.html") as file:
            data = file.read()

        response = make_response(data, 200)

        response.headers["Content-Type"] = "text/html; charset=utf-8"

        return response