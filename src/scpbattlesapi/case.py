from flask import make_response, request, jsonify
from flask_restful import Resource

from config import Config
from helpers.add_item import add_item
from helpers.consume_item import consume_item
from helpers.get_inventory import get_inventory

class Case(Resource):

    def post(self):
        
        with Config() as config:
            steam_api_key = config["steam_api_key"]
        
        steam_id = request.args.get["steam_id"]
        key_item_id = request.args.get("key_item_id")
        case_item_id = request.args.get("case_item_id")

        inventory = get_inventory(steam_id, steam_api_key)

        key_item_data = None
        case_item_data = None

        # look for the key item in the inventory and check if it is a key        
        for item in inventory:

            if item["itemid"] != key_item_id:
                continue
            
            if item["itemdefid"] not in config["key_case_map"]:
                response = make_response(
                    jsonify(
                        {
                            "error": "not_key"
                        }
                    ),

                    400
                )

                return response
            
            key_item_data = item
        
        if key_item_data is None:
            response = make_response(
                jsonify(
                    {
                        "error": "key_not_in_inventory"
                    },
                    400
                )
            )
        
        # look for case item in the inventory and check if its a case and matches the key type
        for item in inventory:

            if item["item_id"] != case_item_id:
                continue 
            
            # check if case exists in list of cases that the specified key can open
            if item["itemdefid"] not in config["key_case_map"][key_item_data["itemdefid"]]:
                response = make_response(
                    jsonify(
                        {
                            "error": "key_case_mismatch"
                        },
                        400
                    )
                )

                return response

            case_item_data = item
        
        if case_item_data is None:
            response = make_response(
                jsonify(
                    {
                        "error": "case_not_in_inventory"
                    },
                    400
                )
            )

            return response



        response = make_response(request.remote_addr, 200)
        response.headers["Response-Type"] = "open_case"

        return response