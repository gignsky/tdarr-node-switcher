from . import tdarr


class Logic:
    @staticmethod
    def refresh_all(Constants):
        # tdarr.Tdarr_Orders.refresh_health_checks(constants)
        tdarr.Tdarr_Orders.update_failed_transcodes(constants)
