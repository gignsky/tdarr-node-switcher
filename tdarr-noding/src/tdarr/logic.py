import requests
import json


class Tdarr_Logic:
    @staticmethod
    def generic_get_nodes(Server):
        """
        generic_get_nodes requests.get get_nodes_output

        Args:
            Server (Class): basic server class

        Returns:
            json_response: from requests.get
        < Document Guardian | Protect >
        """
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
    #             all_alive_node_dicts.append(inner_dictionary) #TODO START HERE WHEN GETTING BACK AT IT - OLD
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
    def find_nodes_with_work(Server):
        """
        find_nodes_with_work find a list of nodes with and without work

        Args:
            Server (Class): basic server class

        Returns:
            list_of_nodes_with_work (list): list of nodes with work
            list_of_nodes_without_work (list): list of nodes without work
        < Document Guardian | Protect >
        """
        json_response = Tdarr_Logic.generic_get_nodes(Server)

        list_of_nodes_with_work = []
        list_of_nodes_without_work = []

        for node_id in json_response:
            node_id_inner_dictionary = json_response[node_id]

            worker_dict = node_id_inner_dictionary["workers"]
            legnth = len(worker_dict)

            if legnth == 0:
                list_of_nodes_without_work.append(node_id_inner_dictionary["nodeName"])
            else:
                list_of_nodes_with_work.append(node_id_inner_dictionary["nodeName"])

        return list_of_nodes_with_work, list_of_nodes_without_work

    # searching...
    @staticmethod
    def search_for_failed_health_checks(Server):
        """
        search_for_failed_health_checks search for failed health checks

        Args:
            Server (Class): basic server class

        Returns:
            list_of_failed_health_checks
        < Document Guardian | Protect >
        """
        payload, headers = Tdarr_Logic.payload_and_headers_file_modification("error")

        response = requests.post(
            Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        fails = []
        for i in response:
            node_id = i.get("_id")

            health_check_status = i.get("HealthCheck")
            # print(healthCheckStatus)
            if health_check_status == "Error":
                fails.append(node_id)
                # print(i)

        return fails

    @staticmethod
    def search_for_failed_transcodes(Server):
        """
        search_for_failed_transcodes search for failed health checks

        Args:
            Server (Class): basic server class

        Returns:
            list_of_transcode_fails
        < Document Guardian | Protect >
        """
        payload, headers = Tdarr_Logic.payload_and_headers_file_modification(
            "Transcode error"
        )

        response = requests.post(
            Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcode_errors = []
        for i in response:
            node_id = i.get("_id")

            transcode_errors.append(node_id)
            # print(i)

        return transcode_errors

    @staticmethod
    def search_for_successful_transcodes(Server):
        """
        search_for_successful_transcodes search for failed successful transcodes

        Args:
            Server (Class): basic server class

        Returns:
            transcodes successes (list)
        < Document Guardian | Protect >
        """
        payload, headers = Tdarr_Logic.payload_and_headers_file_modification(
            "Transcode success"
        )

        response = requests.post(
            Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcode_successes = []
        for i in response:
            node_id = i.get("_id")

            transcode_successes.append(node_id)
            # print(i)

        return transcode_successes

    @staticmethod
    def search_for_queued_transcodes(Server):
        """
        search_for_queued_transcodes search for transcodes still queued

        Args:
            Server (Class): basic server class

        Returns:
            transcodes_queued (list)
        < Document Guardian | Protect >
        """
        payload, headers = Tdarr_Logic.payload_and_headers_file_modification("Queued")

        response = requests.post(
            Server.search, json=payload, headers=headers, timeout=1.5
        )

        response = json.loads(response.text)

        # print(len(response))
        transcode_queued = []
        for i in response:
            node_id = i.get("_id")
            if i.get("TranscodeDecisionMaker") == "Queued":
                transcode_queued.append(node_id)
        print(transcode_queued)

        return transcode_queued

    @staticmethod
    def payload_and_headers_file_modification(string):
        """
        payload_and_headers_file_modification modify payloads and headers for most requests.post

        Args:
            string (str): string to insert into payload

        Returns:
            payload, headers: for request.post
        < Document Guardian | Protect >
        """
        payload = {
            "data": {
                "string": string,
                "lessThanGB": 100,
                "greaterThanGB": 0,
            }
        }
        headers = {"Content-Type": "application/json"}
        return payload, headers

    @staticmethod
    def payload_and_headers_worker_modification(
        node_id, increase_or_decrease, worker_type
    ):
        """
        payload_and_headers_worker_modification payload creator for worker modification

        Args:
            node_id (string): id string of node
            increase_or_decrease (string): increase or decrease the amount of workers
            worker_type (string/list): if string it will execute on that node worker alone if a list it will retrun a list of payloads for all items in list

        Returns:
            json: payload for request.post to be used later
        < Document Guardian | Protect >
        """
        headers = {"Content-Type": "application/json"}
        # if worker_type == list(worker_type):
        #     final_payload=[]
        #     for item in worker_type:
        #         payload = {"data":{"nodeID": node_id,"process": increase_or_decrease,"workerType": item}}
        #         final_payload.append(payload)
        # else:
        final_payload = {
            "data": {
                "nodeID": node_id,
                "process": increase_or_decrease,
                "workerType": worker_type,
            }
        }
        return final_payload, headers

    ##discover up or down by set to level
    @staticmethod
    def get_direction(set_to_level, worker_type, NodeClass=None):
        """
        get_direction finds the direction to increase or decrease the current value

        Args:
            set_to_level (int): numeric value of which to set the direction towards
            worker_type (string): string regarding which worker to focus on
            list_of_worker_types (list, optional): if adjusting all place a list of all worker types or those to be adjusted in this field. Defaults to None.

        Returns:
            string: 'increase' or 'decrease'
        < Document Guardian | Protect >
        """
        if set_to_level == 0:
            increase_or_decrease = "decrease"
        else:
            # if worker_type == "All":
            #     if list_of_worker_types is not None:
            #         list_of_up_downs = []
            #         for worker_type in list_of_worker_types:
            #             if worker_type == "healthcheckcpu":
            #                 current_level = NodeClass.current_cpu_healthcheck
            #             elif worker_type == "healthcheckgpu":
            #                 current_level = NodeClass.current_gpu_healthcheck
            #             elif worker_type == "transcodecpu":
            #                 current_level = NodeClass.current_cpu_transcode
            #             elif worker_type == "transcodegpu":
            #                 current_level = NodeClass.current_gpu_transcode
            #             if current_level > set_to_level:
            #                 direction = "decrease"
            #             elif current_level == set_to_level:
            #                 direction = "Hold"
            #             elif current_level < set_to_level:
            #                 direction = "increase"
            #             list_of_up_downs.append(direction)
            #     increase_or_decrease = list_of_up_downs
            # else:
            if worker_type == "healthcheckcpu":
                current_level = NodeClass.current_cpu_healthcheck
            elif worker_type == "healthcheckgpu":
                current_level = NodeClass.current_gpu_healthcheck
            elif worker_type == "transcodecpu":
                current_level = NodeClass.current_cpu_transcode
            elif worker_type == "transcodegpu":
                current_level = NodeClass.current_gpu_transcode
            if current_level > set_to_level:
                direction = "decrease"
            elif current_level == set_to_level:
                direction = "Hold"
            elif current_level < set_to_level:
                direction = "increase"

            # if worker_type=="All":
            #     increase_or_decrease=list_of_up_downs
            # else:
            increase_or_decrease = direction

        return increase_or_decrease
