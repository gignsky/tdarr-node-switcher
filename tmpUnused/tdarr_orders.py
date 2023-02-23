from . import requests
from . import json


class Tdarr_Orders:
    @staticmethod
    def getNodes(GET_NODES):
        """gets current nodes on tdarr

        Returns:
            thing: unformatted json
        """

        var = requests.get(GET_NODES)

        return var

    @staticmethod
    def search_for_failed_health_checks():
        payload = {
            "data": {
                "string": "Error",
                "lessThanGB": 100,
                "greaterThanGB": 0,
            }
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(SEARCH, json=payload, headers=headers)

        response = json.loads(response.text)

        # print(len(response))
        fails = []
        for i in response:
            id = i.get("_id")

            healthCheckStatus = i.get("HealthCheck")
            # print(healthCheckStatus)
            if healthCheckStatus == "Error":
                fails.append(id)
                # print(i)

        return fails

    @staticmethod
    # mod workers darr-node
    def darrWorkerMod(url, runs, increaseOrDecrease, worker):
        if increaseOrDecrease == "up":
            change = "increase"
        elif increaseOrDecrease == "down":
            change = "decrease"

        if worker == "healthCPU":
            workerType = "healthcheckcpu"
        elif worker == "transcodeCPU":
            workerType = "transcodecpu"

        # actual logic
        i = 0
        while i != runs:
            payload = {
                "data": {
                    "nodeID": "darr-Node",
                    "process": change,
                    "workerType": workerType,
                }
            }
            headers = {"Content-Type": "application/json"}

            requests.post(url, json=payload, headers=headers)

            i = i + 1

    # update orders
    @staticmethod
    def update_failed_transcodes():
        ids = search_for_failed_transcodes_checks()

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

            requests.post(UPDATE_URL, json=payload, headers=headers)

            # pprint(response)

    @staticmethod
    def update_health_checks():
        ids = search_for_failed_health_checks()

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

            requests.post(UPDATE_URL, json=payload, headers=headers)

            # pprint(response)

    @staticmethod
    def search_for_successful_transcodes_checks():
        payload = {
            "data": {
                "string": "Transcode success",
                "lessThanGB": 100,
                "greaterThanGB": 0,
            }
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(SEARCH, json=payload, headers=headers)

        response = json.loads(response.text)

        # print(len(response))
        transcodeSuccesses = []
        for i in response:
            id = i.get("_id")

            transcodeSuccesses.append(id)
            # print(i)

        return transcodeSuccesses

    @staticmethod
    def update_currently_processing(UPDATE_URL):
        ids = search_for_successful_transcodes_checks()

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

            requests.post(UPDATE_URL, json=payload, headers=headers)

            # pprint(response)
