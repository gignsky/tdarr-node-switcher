import requests
import yaml
from . import tdarr
# from . import status_tracking


class Logic:
    @staticmethod
    def refresh_all(constants):
        print("Refreshing...")
        tdarr.Tdarr_Orders.refresh_health_checks(constants)
        tdarr.Tdarr_Orders.update_transcodes(constants)

    @staticmethod
    def server_status_check(Server):
        var = requests.get(Server.status)

        if var.status_code != 200:
            return "stop"
        else:
            print("INFO: Server is ALIVE!")
            return "alive"

    @staticmethod
    def script_status(path):
        try:
            if path.is_file():
                with open(path, "r") as file:
                    status_file = yaml.safe_load(file)
                    return status_file
            else:
                return "Empty"
        except AttributeError:
            return "Empty"

    # @staticmethod
    # def setup_status_class(status_file):
    #     StatusClass = status_tracking.StatusClass(status_file)
