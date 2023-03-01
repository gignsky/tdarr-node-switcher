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
        payload, headers = Tdarr_Logic.payload_and_headers_file_modification("error")

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
        payload, headers = Tdarr_Logic.payload_and_headers_file_modification("Transcode error")

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
        payload, headers = Tdarr_Logic.payload_and_headers_file_modification("Transcode success")

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
    def payload_and_headers_file_modification(string):
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
    def payload_and_headers_worker_modification(node_id,increase_or_decrease,worker_type):
        headers = {"Content-Type": "application/json"}
        if worker_type == list(worker_type):
            final_payload=[]
            for item in worker_type:
                payload = {"data":{"nodeID": node_id,"process": increase_or_decrease,"workerType": item}}
                final_payload.append(payload)
        else:
            final_payload = {
                "nodeID": node_id,
                "process": increase_or_decrease,
                "workerType": worker_type
            }
        return final_payload, headers

    @staticmethod
    def reset_workers_to_zero(Server,node_dictionary):
        #iterate through nodes
        for name in node_dictionary:
            NodeClass=node_dictionary[name]
            if NodeClass.online:
                Tdarr_Logic.set_worker_level(Server,NodeClass,0,"All")

    @staticmethod
    def set_worker_level(Server,NodeClass,set_to_level,workerType):
        #get node info
        node_id=NodeClass.id_string


        ##set worker type
        if workerType =="All":
            list_of_worker_types=["healthcheckcpu","healthcheckgpu","transcodecpu","transcodegpu"]
            direction=Tdarr_Logic.get_direction(set_to_level,workerType,list_of_worker_types)
        else:
            direction=Tdarr_Logic.get_direction(set_to_level,workerType)

        if direction != "Hold":
            if workerType=="All":
                list_of_payload,headers=Tdarr_Logic.payload_and_headers_worker_modification(node_id,direction,list_of_worker_types)
            else:
                payload,headers=Tdarr_Logic.payload_and_headers_worker_modification(node_id,direction,workerType)

        if workerType=="All":
            for payload in list_of_payload:
                response = requests.post(
                Server.mod_worker_limit, json=payload, headers=headers, timeout=1.5
                )
        else:
            response = requests.post(
            Server.mod_worker_limit, json=payload, headers=headers, timeout=1.5
            )


    ##discover up or down by set to level
    @staticmethod
    def get_direction(set_to_level, workerType, list_of_worker_types=None):
        if set_to_level == 0:
            increase_or_decrease = "decrease"
        else:
            if workerType == "All":
                if list_of_worker_types is not None:
                    list_of_up_downs = []
                    for worker_type in list_of_worker_types:
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
                        list_of_up_downs.append(direction)
                increase_or_decrease = list_of_up_downs
            else:
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
                elif current_level==set_to_level:
                    direction="Hold"
                elif current_level < set_to_level:
                    direction="increase"

                if workerType=="All":
                    increase_or_decrease=list_of_up_downs
                else:
                    increase_or_decrease=direction

        return increase_or_decrease
