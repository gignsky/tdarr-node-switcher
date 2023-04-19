import requests
from . import Tdarr_Logic


class Tdarr_Orders:
    # refreshing orders
    @staticmethod
    def refresh_health_checks(Server):
        """
        refresh_health_checks orders a refresh of health checks that have failed

        Args:
            Server (Class): basic server class
        < Document Guardian | Protect >
        """
        ids = Tdarr_Logic.search_for_failed_health_checks(Server)

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

            requests.post(Server.update_url, json=payload, headers=headers, timeout=10)

            # pprint(response)

    @staticmethod
    def update_transcodes(Server):
        """
        update_transcodes update failed transcodes to queued

        Args:
            Server (Class): basic server class
        < Document Guardian | Protect >
        """
        failed_transcodes = Tdarr_Logic.search_for_failed_transcodes(Server)
        succesful_transcodes = Tdarr_Logic.search_for_successful_transcodes(Server)

        lists_of_lists = [failed_transcodes, succesful_transcodes]
        for transcode_list in lists_of_lists:
            for id_number in transcode_list:
                payload = {
                    "data": {
                        "collection": "FileJSONDB",
                        "mode": "update",
                        "docID": id_number,
                        "obj": {"TranscodeDecisionMaker": "Queued"},
                    }
                }
                headers = {"Content-Type": "application/json"}

                requests.post(
                    Server.update_url, json=payload, headers=headers, timeout=10
                )

            # pprint(response)

    @staticmethod
    def mod_worker_limit(Server, headers, payload):
        """
        mod_worker_limit modify worker limit order

        Args:
            Server (Class): basic server class
            headers (basic headers): basic headers
            payload (basic payload): basic payload

        Returns:
            response (json_dict): response from requests.post
        < Document Guardian | Protect >
        """
        response = requests.post(
            Server.mod_worker_limit, json=payload, headers=headers, timeout=10
        )

        return response

    @staticmethod
    def set_worker_level(Server, NodeClass, set_to_level, worker_type):
        """
        set_worker_level actually sets the worker level of a node to desired amount

        Args:
            Server (class): Server Class with endpoints
            NodeClass (class): individual node class
            set_to_level (int): the numeric desired to be achieved by this function
            worker_type (string): type of worker to adjust in format of transcode/healthcheck cpu/gpu all in one word
        < Document Guardian | Protect >
        """
        # get node info
        node_id = NodeClass.id_string

        ##set worker type
        # if worker_type =="All":
        #     list_of_worker_types=["healthcheckcpu","healthcheckgpu","transcodecpu","transcodegpu"]
        #     direction=Tdarr_Logic.get_direction(set_to_level,worker_type,list_of_worker_types)
        # else:
        direction = Tdarr_Logic.get_direction(set_to_level, worker_type, NodeClass)

        if direction != "Hold":
            # if worker_type=="All":
            #     list_of_payload,headers=Tdarr_Logic.payload_and_headers_worker_modification(node_id,direction,list_of_worker_types)
            # else:
            payload, headers = Tdarr_Logic.payload_and_headers_worker_modification(
                node_id, direction, worker_type
            )

            # if worker_type=="All":
            #     for payload in list_of_payload:
            #         response=Tdarr_Orders.mod_worker_limit(Server, headers, payload)
            # else:
            Tdarr_Orders.mod_worker_limit(Server, headers, payload)

    @staticmethod
    def reset_workers_to_zero(Server, node_name, node_dictionary):
        """
        reset_workers_to_zero resets nodes to zero workers in each category

        Args:
            Server (class): Server Class with all relevent endpoints
            node_dictionary (dictionary of classes): dictionary with classes associated with the node names
        < Document Guardian | Protect >
        """
        # iterate through nodes
        for name, NodeClass in node_dictionary.items():
            if node_name == name:
                if NodeClass.online:
                    if NodeClass.current_cpu_transcode != 0:
                        for i in range(NodeClass.current_cpu_transcode):
                            Tdarr_Orders.set_worker_level(
                                Server, NodeClass, 0, "transcodecpu"
                            )
                            print(
                                f"INFO: Ordering '{name}' to decrease transcodecpu workers to 0; try #{i}"
                            )
                    if NodeClass.current_gpu_transcode != 0:
                        for i in range(NodeClass.current_gpu_transcode):
                            Tdarr_Orders.set_worker_level(
                                Server, NodeClass, 0, "transcodegpu"
                            )
                            print(
                                f"INFO: Ordering '{name}' to decrease transcodegpu workers to 0; try #{i}"
                            )
                    if NodeClass.current_cpu_healthcheck != 0:
                        for i in range(NodeClass.current_cpu_healthcheck):
                            Tdarr_Orders.set_worker_level(
                                Server, NodeClass, 0, "healthcheckcpu"
                            )
                            print(
                                f"INFO: Ordering '{name}' to decrease healthcheckcpu workers to 0; try #{i}"
                            )
                    if NodeClass.current_gpu_healthcheck != 0:
                        for i in range(NodeClass.current_gpu_healthcheck):
                            Tdarr_Orders.set_worker_level(
                                Server, NodeClass, 0, "healthcheckgpu"
                            )
                            print(
                                f"INFO: Ordering '{name}' to decrease healthcheckgpu workers to 0; try #{i}"
                            )

    @staticmethod
    def reset_workers_to_max_limits(Server, node_name, node_dictionary):
        """
        reset_workers_to_max_limits set workers to their maximum limits inside of the node'c class

        Args:
            Server (Class): basic server class
            node_name (str): node name to modify
            node_dictionary (dict): dict with node names and their associated dicts
        < Document Guardian | Protect >
        """
        # iterate through nodes
        for name, NodeClass in node_dictionary.items():
            if node_name == name:
                if NodeClass.online:
                    if NodeClass.transcode_max_cpu != 0:
                        for i in range(NodeClass.transcode_max_cpu):
                            Tdarr_Orders.set_worker_level(
                                Server,
                                NodeClass,
                                NodeClass.transcode_max_cpu,
                                "transcodecpu",
                            )
                            print(
                                f"INFO: Ordering '{name}' to increase transcodecpu workers from {NodeClass.current_cpu_transcode} to {NodeClass.transcode_max_cpu}; try #{i}"
                            )
                    if NodeClass.transcode_max_gpu != 0:
                        for i in range(NodeClass.transcode_max_gpu):
                            Tdarr_Orders.set_worker_level(
                                Server,
                                NodeClass,
                                NodeClass.transcode_max_gpu,
                                "transcodegpu",
                            )
                            print(
                                f"INFO: Ordering '{name}' to increase transcodegpu workers from {NodeClass.current_gpu_transcode} to {NodeClass.transcode_max_gpu}; try #{i}"
                            )
                    if NodeClass.healthcheck_max_cpu != 0:
                        for i in range(NodeClass.healthcheck_max_cpu):
                            Tdarr_Orders.set_worker_level(
                                Server,
                                NodeClass,
                                NodeClass.healthcheck_max_cpu,
                                "healthcheckcpu",
                            )
                            print(
                                f"INFO: Ordering '{name}' to increase healthcheckcpu workers from {NodeClass.current_cpu_healthcheck} to {NodeClass.healthcheck_max_cpu}; try #{i}"
                            )
                    if NodeClass.healthcheck_max_gpu != 0:
                        for i in range(NodeClass.healthcheck_max_gpu):
                            Tdarr_Orders.set_worker_level(
                                Server,
                                NodeClass,
                                NodeClass.healthcheck_max_gpu,
                                "healthcheckgpu",
                            )
                            print(
                                f"INFO: Ordering '{name}' to increase healthcheckgpu workers from {NodeClass.current_gpu_healthcheck} to {NodeClass.healthcheck_max_gpu}; try #{i}"
                            )
