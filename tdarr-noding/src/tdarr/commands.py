from . import requests
from . import Tdarr_Logic


class Tdarr_Orders:
    # refreshing orders
    @staticmethod
    def refresh_health_checks(Constants):
        ids = Tdarr_Logic.search_for_failed_health_checks(Constants)

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

            requests.post(Constants.UPDATE_URL, json=payload, headers=headers)

            # pprint(response)

