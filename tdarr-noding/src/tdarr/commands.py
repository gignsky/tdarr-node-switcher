import requests


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

            requests.post(
                constants.Server.update_url, json=payload, headers=headers, timeout=1.5
            )

            # pprint(response)

    @staticmethod
    def update_transcodes(constants):
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

            requests.post(
                constants.Server.update_url, json=payload, headers=headers, timeout=1.5
            )

            # pprint(response)

    @staticmethod
    def mod_worker_limit(Server, headers, payload):
        response = requests.post(
                Server.mod_worker_limit, json=payload, headers=headers, timeout=1.5
                )

        return response
