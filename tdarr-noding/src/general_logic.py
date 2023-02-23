import requests
import yaml
from pathlib import Path
from . import tdarr


class Logic:
    @staticmethod
    def refresh_all(constants):
        print("Refreshing...")
        tdarr.Tdarr_Orders.refresh_health_checks(constants)
        tdarr.Tdarr_Orders.update_failed_transcodes(constants)
        tdarr.Tdarr_Orders.update_successful_transcodes(constants)

    @staticmethod
    def server_status_check(constants):
        var = requests.get(constants.Server.status)

        if var.status_code != 200:
            return "stop"
        else:
            print("INFO: Server is ALIVE!")
            return "alive"

    @staticmethod
    def script_status(constants):
        path = Path(f"{constants.program_folder_path}/running.yml")

        if path.is_file():
            with open(path, "r") as file:
                status = yaml.safe_load(file)
                return status
        else:
            return "Stopped"
