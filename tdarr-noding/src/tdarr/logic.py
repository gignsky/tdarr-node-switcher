import requests
import json


class Tdarr_Logic:
    # find alive nodes
    @staticmethod
    def alive_node_search(constants):
        """gets current nodes on tdarr

        Returns:
            thing: unformatted json
        """

        response = requests.get(constants.GET_NODES)

        # loads response into json beautifier
        json_response = json.loads(response.text)

        # establish empty lists
        expected_node_status = (
            []
        )  # TODO work on a way of getting all nodes names out of the config file in the constant creator section to apply to this function

        # find node dict ids
        node_ids = []
        for id in json_response:
            node_ids.append(id)

        # find node names per id
        all_alive_node_names = []
        all_alive_node_dicts = []
        for id in node_ids:
            inner_dictionary = json_response[id]
            name = inner_dictionary["nodeName"]
            all_alive_node_names.append(name)
            all_alive_node_dicts.append(inner_dictionary)

        return all_alive_node_names, all_alive_node_dicts

    @staticmethod
    def nodeTest(node_name, dictionary):
        node_names_list = Logic.list_of_node_names(dictionary)
        if node_name in node_names_list:
            tdarr_node_online_status = "Online"
        else:
            tdarr_node_online_status = "Offline"

        return tdarr_node_online_status

    # searching...
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
