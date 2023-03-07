import yaml


class Config:

    def __init__(self, config_path="/etc/scpbattlesapi/config.yaml"):

        self.config_path=config_path
        self.dict=None

    def __enter__(self):

        # load database upon entering context
        with open(self.config_path, "r") as file:
            db_dict = yaml.safe_load(file)
        
        self.dict = db_dict

        return self.dict

    def __exit__(self, exception_type, exception_value, traceback):

        pass
            