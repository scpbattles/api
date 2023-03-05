import tomlkit


class Config:

    def __init__(self, config_path="/var/local/scpbattlesapi/database.json"):

        self.config_path=config_path
        self.dict=None

    def __enter__(self):

        # load database upon entering context
        with open(self.config_path, "r") as file:
            db_dict = tomlkit.load(file)
        
        self.dict = db_dict

        return self.dict

    def __exit__(self, exception_type, exception_value, traceback):

        pass
            