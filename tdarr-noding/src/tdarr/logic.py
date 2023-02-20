import requests
import json


class Tdarr_Logic:
    @staticmethod
    def search_for_failed_health_checks(constants):
        payload = {
            "data": {
                "string": "Error",
                "lessThanGB": 100,
                "greaterThanGB": 0,
            }
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            constants.SEARCH, json=payload, headers=headers, timeout=1.5
        )

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
    def search_for_failed_transcodes(constants):
        payload = {
            "data": {
                "string": "Transcode error",
                "lessThanGB": 100,
                "greaterThanGB": 0,
            }
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            constants.SEARCH, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcodeErrors = []
        for i in response:
            id = i.get("_id")

            transcodeErrors.append(id)
            # print(i)

        return transcodeErrors

    @staticmethod
    def search_for_successful_transcodes(constants):
        payload = {
            "data": {
                "string": "Transcode success",
                "lessThanGB": 100,
                "greaterThanGB": 0,
            }
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            constants.SEARCH, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcodeSuccesses = []
        for i in response:
            id = i.get("_id")

            transcodeSuccesses.append(id)
            # print(i)

        return transcodeSuccesses
