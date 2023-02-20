import requests
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
        var = requests.get(constants.STATUS)

        if var.status_code != 200:
            return "stop"
        else:
            return "alive"
