import yaml


class YAMLHandler:

    def __init__(self, file_path):

        self.file_path = file_path
        self.dict=None

    def __enter__(self):

        # load file upon entering context
        with open(self.file_path, "r") as file:
            self.dict = yaml.safe_load(file)

        return self.dict

    def __exit__(self, exception_type, exception_value, traceback):

        # save the file upon exiting context
        with open(self.file_path, "w") as file:
            yaml.dump(self.dict, file)
            