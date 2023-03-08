import yaml


class Database:

    def __init__(self, db_path="/var/local/scpbattlesapi/database.yaml"):

        self.db_path=db_path
        self.dict=None

    def __enter__(self):

        # load database upon entering context
        with open(self.db_path, "r") as file:
            db_dict = yaml.safe_load(file)
        
        self.dict = db_dict

        return self.dict

    def __exit__(self, exception_type, exception_value, traceback):

        # save the database upon exiting context
        with open(self.db_path, "w") as file:
            yaml.dump(self.dict, file)
            