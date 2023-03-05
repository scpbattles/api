import random

from flask import make_response, request, jsonify
from flask_restful import Resource
from requests import HTTPError

from config import Config
from steamapi.add_item import add_item
from steamapi.consume_item import consume_item
from steamapi.get_inventory import get_inventory

class Case(Resource):

    def post(self):
        
        with Config() as config:
            steam_api_key = config["steam_api_key"]
            case_probabilities = config["case_probabilities"]
        
        steam_id = request.args.get["steam_id"]
        key_item_id = request.args.get("key_item_id")
        case_item_id = request.args.get("case_item_id")

        if steam_id is None:
            return "Missing steam_id query parameter", 400
        if key_item_id is None:
            return "Missing key_item_id query parameter", 400
        if case_item_id is None:
            return "Missing case_item_id query parameter", 400

        try:
            inventory = get_inventory(steam_id, steam_api_key)
            
        except HTTPError:
            return "Failed to fetch inventory", 500

        key_item_data = None
        case_item_data = None

        # look for the key item in the inventory and check if it is a key        
        for item in inventory:

            if item["itemid"] != key_item_id:
                continue
            
            if item["itemdefid"] not in config["key_case_map"]:
                return "Specified key is not a key", 400
            
            key_item_data = item
        
        if key_item_data is None:
            return "Specified key not in inventory", 400
        
        # look for case item in the inventory and check if its a case and matches the key type
        for item in inventory:

            if item["itemid"] != case_item_id:
                continue 
            
            # check if case exists in list of cases that the specified key can open
            if item["itemdefid"] not in config["key_case_map"][key_item_data["itemdefid"]]:
                return "Specified case does not match specified key", 400

            case_item_data = item
        
        if case_item_data is None:
            return "Specified case not in inventory", 400

        random_number = random.randint(1, 10000)

        # get probabilities for this case
        item_group_probabilities = case_probabilities[case_item_data["itemdefid"]]

        # random number height is the highest the random number can be to get those items
        for random_number_height in item_group_probabilities.keys():
            
            # if our random number is lower than this item group's number height, we stop
            if random_number <= int(random_number_height):
                possible_items = case_probabilities[random_number_height]
            
            # if it was higher we go to the next number height
            else:
                continue 
        
        awarded_item = random.choice(possible_items)

        try:
            # consume key
            consume_item(
                item_id=key_item_data["itemid"],
                steam_id=steam_id,
                steam_api_key=steam_api_key
            )
        
        except HTTPError:
            return "Failed to consume key item", 500
        
        try: 
            # consume case
            consume_item(
                item_id=case_item_data["itemid"],
                steam_id=steam_id,
                steam_api_key=steam_api_key
            )
        
        except HTTPError:
            return "Failed to consume case item", 500

        try:
            # give awarded item
            add_item(
                item_def=awarded_item,
                steam_id=steam_id,
                steam_api_key=steam_api_key
            )
        
        except HTTPError:
            return "Failed to give award item", 500

        response = make_response(
            jsonify(
                {
                    "awarded_item": awarded_item,
                    "random_number": random_number
                }
            )
        )
        response.headers["Response-Type"] = "open_case"

        return response