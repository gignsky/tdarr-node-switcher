from . import tdarr


class Logic:
    @staticmethod
    def refresh_all(constants):
        print("Refreshing...")
        tdarr.Tdarr_Orders.refresh_health_checks(constants)
        tdarr.Tdarr_Orders.update_failed_transcodes(constants)
        tdarr.Tdarr_Orders.update_successful_transcodes(constants)
