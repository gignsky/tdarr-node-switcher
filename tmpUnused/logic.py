from . import exists
from . import requests
from . import json
from pathlib import Path
from . import Tdarr_Orders


class Logic:
    @staticmethod
    def status(STATUS):
        var = requests.get(STATUS)

        if var.status_code != 200:
            print("Tdarr NOT alive!")
            return "stop"

    @staticmethod
    def discoverSituation(GET_NODES):
        """discovers the current situation for ganoslal node

        Returns:
            situation: string (either "starting" or "stopping")
        """

        var = Tdarr_Orders.getNodes(GET_NODES)

        # load into json format
        jsonVar = json.loads(var.text)
        # pprint(jsonVar)

        # figures out the situation
        situation = Logic.nodeLogic(jsonVar)

        return situation

    @staticmethod
    def nodeLogic(get_nodes_output_in_json):
        # assign input to var
        var = get_nodes_output_in_json

        # find if both are working and online
        darr = Logic.nodeTest("server-node", var)
        ganosLal = Logic.nodeTest("ganosLal", var)
        file_check = exists("/root/tdarr-node-switcher/running")

        # testing of output for test modules
        # pprint("darr: " + darr)
        # pprint("GanosLal: " + ganosLal)

        if file_check == True:
            if ganosLal == "Online":
                return "running"

            elif ganosLal == "Offline":
                return "stopping"

            elif darr == "Online":
                mod_darr_node("down")
                return "broken"

        elif file_check == False:
            if ganosLal == "Offline":
                return "stopped"

            elif ganosLal == "Online":
                Path(
                    "/home/gig/local_repos/tdarr-node-switcher/running"
                ).touch()  # TODO Make changeable to current system and have file be placed in current directory
                return "starting"

    @staticmethod
    def list_of_node_names(var):
        list_of_var_keys = []
        for i in var:
            list_of_var_keys.append(i)

        list_of_node_names = []
        for i in list_of_var_keys:
            dict_item = var[i]
            list_of_node_names.append(dict_item["nodeName"])

        return list_of_node_names

    @staticmethod
    def nodeTest(node_name, dictionary):
        node_names_list = Logic.list_of_node_names(dictionary)
        if node_name in node_names_list:
            tdarr_node_online_status = "Online"
        else:
            tdarr_node_online_status = "Offline"

        return tdarr_node_online_status

    @staticmethod
    def mod_darr_node(upOrDown):
        if upOrDown == "up":
            # start_node
        # Startup Darr Node
        Tdarr_Orders.darrWorkerMod(MOD_WORKER_LIMIT, DARR_NODE_HEALTH_NODES, upOrDown, "healthCPU")
        Tdarr_Orders.darrWorkerMod(MOD_WORKER_LIMIT, DARR_NODE_TRANSCODE_NODES, upOrDown, "transcodeCPU")
        if upOrDown == "down":
            Tdarr_Orders.update_currently_processing()
            # stop_node
