from flask import make_response, request
from flask_restful import Resource


class Address(Resource):

    def get(self):
        response = make_response(request.remote_addr, 200)
        response.headers["Response-Type"] = "get_ip"

        return response