import os
from typing import List, Dict, Type

from scpbattlesapi.yamlhandler import YAMLHandler
from scpbattlesapi.steamapi import Item

class ConfigHandler:
    def __init__(self, config_path: str, bad_words_path: str):

        if not os.path.exists(config_path):
            raise FileNotFoundError("Specified config file path does not exist")
        
        if not os.path.exists(bad_words_path):
            raise FileNotFoundError("Specified bad words file path does not exist")
        
        self.config_path = config_path
        self.bad_words_path = bad_words_path
    
    @property
    def default_items(self) -> List[int]:
        with YAMLHandler(self.config_path) as config:
            default_items = config["default_items"]

        return default_items
    
    @property
    def case_probabilites(self) -> Dict[int, Dict[int, int]]:
        with YAMLHandler(self.config_path) as config:
            case_probabilities = config["case_probabilities"]
        
        return case_probabilities
    
    @property
    def item_model_map(self) -> Dict[int, Type[Item]]:

        with YAMLHandler(self.config_path) as config:
            item_model_map = config["item_model_map"]

        return item_model_map

    @property
    def case_key_map(self) -> Dict[int, List[int]]:
        with YAMLHandler(self.config_path) as config:
            case_key_map = config["case_key_map"]
        
        return case_key_map
    
    @property
    def crafting_recipes(self) -> Dict[int, List[int]]:
        with YAMLHandler(self.config_path) as config:
            crafting_recipes = config["crafting_recipes"]
        
        return crafting_recipes