import yaml
class Logic:
    @staticmethod
    def script_status(path):
        if path.is_file():
            with open(path, "r") as file:
                status_file = yaml.safe_load(file)
                return status_file
        else:
            return "Stopped"
