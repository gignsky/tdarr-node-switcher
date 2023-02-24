import requests
import json


class Tdarr_Logic:
    @staticmethod
    def generic_get_nodes(Server):
        response = requests.get(Server.get_nodes)

        # loads response into json beautifier
        json_response = json.loads(response.text)

        return json_response

    # find nodes with ongoing work
    @staticmethod
    def find_nodes_with_work(Server):
        json_response = Tdarr_Logic.generic_get_nodes(Server)

        list_of_nodes_with_work = []

        for node_id in json_response:
            node_id_inner_dictionary = json_response[node_id]

            worker_dict = node_id_inner_dictionary["workers"]
            legnth = len(worker_dict)

            if legnth == 0:
                # TODO add pause node function
                print("PLACEHOLDER")
            else:
                list_of_nodes_with_work.append(node_id_inner_dictionary["nodeName"])

        return list_of_nodes_with_work

    # searching...
    @staticmethod
    def search_for_failed_health_checks(Server):
        payload, headers = Tdarr_Logic.payload_and_headers("error")

        response = requests.post(
            Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        fails = []
        for i in response:
            node_id = i.get("_id")

            healthCheckStatus = i.get("HealthCheck")
            # print(healthCheckStatus)
            if healthCheckStatus == "Error":
                fails.append(node_id)
                # print(i)

        return fails

    @staticmethod
    def search_for_failed_transcodes(Server):
        payload, headers = Tdarr_Logic.payload_and_headers("Transcode error")

        response = requests.post(
            Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcodeErrors = []
        for i in response:
            node_id = i.get("_id")

            transcodeErrors.append(node_id)
            # print(i)

        return transcodeErrors

    @staticmethod
    def search_for_successful_transcodes(Server):
        payload, headers = Tdarr_Logic.payload_and_headers("Transcode success")

        response = requests.post(
            Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcodeSuccesses = []
        for i in response:
            node_id = i.get("_id")

            transcodeSuccesses.append(node_id)
            # print(i)

        return transcodeSuccesses

    @staticmethod
    def payload_and_headers(string):
        payload = {
            "data": {
                "string": string,
                "lessThanGB": 100,
                "greaterThanGB": 0,
            }
        }
        headers = {"Content-Type": "application/json"}
        return payload, headers
