from . import requests
from . import Tdarr_Logic


class Tdarr_Orders:
    # refreshing orders
    @staticmethod
    def refresh_health_checks(constants):
        ids = Tdarr_Logic.search_for_failed_health_checks(constants)

        i = 0

        for i in ids:
            payload = {
                "data": {
                    "collection": "FileJSONDB",
                    "mode": "update",
                    "docID": i,
                    "obj": {"HealthCheck": "Queued"},
                }
            }
            headers = {"Content-Type": "application/json"}

            requests.post(constants.UPDATE_URL, json=payload, headers=headers, timeout=1.5)

            # pprint(response)

    @staticmethod
    def update_failed_transcodes(constants):
        ids = Tdarr_Logic.search_for_failed_transcodes(constants)

        i = 0

        for i in ids:
            payload = {
                "data": {
                    "collection": "FileJSONDB",
                    "mode": "update",
                    "docID": i,
                    "obj": {"TranscodeDecisionMaker": "Queued"},
                }
            }
            headers = {"Content-Type": "application/json"}

            requests.post(constants.UPDATE_URL, json=payload, headers=headers, timeout=1.5)

            # pprint(response)

