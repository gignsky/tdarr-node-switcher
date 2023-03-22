import requests
from . import Tdarr_Logic


class Tdarr_Orders:
    # refreshing orders
    @staticmethod
    def refresh_health_checks(Server):
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

            requests.post(
                Server.update_url, json=payload, headers=headers, timeout=1.5
            )

            # pprint(response)

    @staticmethod
    def update_transcodes(Server):
        ids = Tdarr_Logic.search_for_failed_transcodes(Server)

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
                Server.update_url, json=payload, headers=headers, timeout=1.5
            )

            # pprint(response)

    @staticmethod
    def mod_worker_limit(Server, headers, payload):
        response = requests.post(
                Server.mod_worker_limit, json=payload, headers=headers, timeout=1.5
                )

        return response

    @staticmethod
    def set_worker_level(Server,NodeClass,set_to_level,worker_type):
        """
        set_worker_level actually sets the worker level of a node to desired amount

        Args:
            Server (class): Server Class with endpoints
            NodeClass (class): individual node class
            set_to_level (int): the numeric desired to be achieved by this function
            worker_type (string): type of worker to adjust in format of transcode/healthcheck cpu/gpu all in one word
        < Document Guardian | Protect >
        """
        #get node info
        node_id=NodeClass.id_string


        ##set worker type
        # if worker_type =="All":
        #     list_of_worker_types=["healthcheckcpu","healthcheckgpu","transcodecpu","transcodegpu"]
        #     direction=Tdarr_Logic.get_direction(set_to_level,worker_type,list_of_worker_types)
        # else:
        direction=Tdarr_Logic.get_direction(set_to_level,worker_type,NodeClass)

        if direction != "Hold":
            # if worker_type=="All":
            #     list_of_payload,headers=Tdarr_Logic.payload_and_headers_worker_modification(node_id,direction,list_of_worker_types)
            # else:
            payload,headers=Tdarr_Logic.payload_and_headers_worker_modification(node_id,direction,worker_type)

        # if worker_type=="All":
        #     for payload in list_of_payload:
        #         response=Tdarr_Orders.mod_worker_limit(Server, headers, payload)
        # else:
            response=Tdarr_Orders.mod_worker_limit(Server, headers, payload)
