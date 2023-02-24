import requests
import json


class Tdarr_Logic:
    @staticmethod
    def generic_get_nodes(Server):
        response = requests.get(Server.get_nodes)

        # loads response into json beautifier
        json_response = json.loads(response.text)

        return json_response

    # find alive nodes
    #     @staticmethod
    #     def alive_node_search(constants):
    #         """gets current nodes on tdarr
    #
    #         Returns:
    #             thing: unformatted json
    # < Document Guardian | Protect >
    #         """
    #         json_response = Tdarr_Logic.generic_get_nodes(constants)
    #
    #         # find node dict ids
    #         node_ids = []
    #         for id in json_response:
    #             node_ids.append(id)
    #
    #         # find node names per id
    #         all_alive_node_names = []
    #         all_alive_node_dicts = []
    #         expected_node_status = {}
    #         for id in node_ids:
    #             inner_dictionary = json_response[id]
    #             name = inner_dictionary["nodeName"]
    #             all_alive_node_names.append(name)
    #             all_alive_node_dicts.append(inner_dictionary) #TODO START HERE WHEN GETTING BACK AT IT
    #             if name in Constants.all_tdarr_nodes:
    #                 expected_node_status[name] = "Online"
    #             else:
    #                 expected_node_status[name] = "Unexpected"
    #                 # WARN UNEXPECTED NODE
    #                 print(
    #                     f"WARNING: Node named: `{name}` was not expected in the configuration file!"
    #                 )
    #
    #         for name in constants.list_of_tdarr_node_names:
    #             if name not in all_alive_node_names:
    #                 expected_node_status[name] = "Offline"
    #
    #         return expected_node_status

#     @staticmethod
#     def nodeTest(node_name, dictionary):
#         node_names_list = Logic.list_of_node_names(dictionary)
#         if node_name in node_names_list:
#             tdarr_node_online_status = "Online"
#         else:
#             tdarr_node_online_status = "Offline"
#
#         return tdarr_node_online_status

    # find nodes with ongoing work
    @staticmethod
    def find_nodes_with_work(constants):
        json_response = Tdarr_Logic.generic_get_nodes(constants)

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
            constants.Server.search, json=payload, headers=headers, timeout=1.5
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
            constants.Server.search, json=payload, headers=headers, timeout=1.5
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
            constants.Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcodeSuccesses = []
        for i in response:
            id = i.get("_id")

            transcodeSuccesses.append(id)
            # print(i)

        return transcodeSuccesses
