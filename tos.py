class TOS(Resource):
    def get(self):
        
        with open("resources/html/tos.html") as file:
            data = file.read()

        response = make_response(data, 200)

        response.headers["Content-Type"] = "text/html; charset=utf-8"

        return response
