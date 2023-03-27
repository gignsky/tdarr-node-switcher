import requests
import yaml
from pathlib import Path
from . import tdarr

# from . import status_tracking


class Logic:
    @staticmethod
    def refresh_all(constants):
        print("Refreshing...")
        tdarr.Tdarr_Orders.refresh_health_checks(constants)
        tdarr.Tdarr_Orders.update_transcodes(constants)

    @staticmethod
    def server_status_check(Server):
        var = requests.get(Server.status)

        if var.status_code != 200:
            return "stop"
        else:
            print("INFO: Server is ALIVE!")
            return "alive"

    @staticmethod
    def script_status(path_str):
        path = Path(path_str)
        if path.is_file():
            with open(path, "r") as file:
                status_file = yaml.safe_load(file)
                return status_file
        else:
            return "Empty"

    #     @staticmethod
    #     def reset_node_workers(Server,node_dictionary,node_name=None):
    #         if node_name is None:
    #             for node in node_dictionary:
    #                 node_class = node_dictionary[node]
    #                 line_state = node_class.online
    #                 if line_state:
    #                     #reset node to zero workers
    #                     tdarr.Tdarr_Orders.reset_workers_to_zero(Server,node,node_dictionary)
    #
    #                     #wait for workers to set to zero
    #                     time.sleep(2.5)
    #
    #                     #reset node to max worker levels
    #                     tdarr.Tdarr_Orders.reset_workers_to_max_limits(Server,node,node_dictionary)
    #         else:
    #             for node in node_dictionary:
    #                 node_class = node_dictionary[node]
    #                 if node_name==node:
    #                     line_state = node_class.online
    #                     if line_state:
    #                         #reset node to zero workers
    #                         tdarr.Tdarr_Orders.reset_workers_to_zero(Server,node,node_dictionary)
    #
    #                         #wait for workers to set to zero
    #                         time.sleep(2.5)
    #
    #                         #reset node to max worker levels
    #                         tdarr.Tdarr_Orders.reset_workers_to_max_limits(Server,node,node_dictionary)

    @staticmethod
    def find_quant_living_nodes(node_dictionary):
        """
        find_quant_living_nodes returns a integer value of total nodes that are alive and connected to the tdarr server

        Args:
            node_dictionary (dictionary): dictionary containing node names and their respective classes

        Returns:
            quantity_of_living_nodes (int): integer value with total number of nodes that are alive and connected to the tdarr server
        < Document Guardian | Protect >
        """
        ##  find quantity of online nodes

        quantity_of_living_nodes = 0
        current_priority_level = 0
        for _, node_class in node_dictionary.items():
            line_state = node_class.online
            priority_level = node_class.priority
            if line_state:
                quantity_of_living_nodes += 1
                if priority_level >= current_priority_level:
                    current_priority_level = priority_level
        return quantity_of_living_nodes

    @staticmethod()
    def find_quantity_of_transcode_workers(node_dictionary, max_nodes):
        # does not count work to be done on primary node unless node is alive
        max_transcode_workers = 0
        is_primary_alive = None
        primary_node_transcode_workers = 0
        is_primary_killable = None
        highest_priority_number = 0
        highest_priority_transcode_workers = 0

        for _, Class in node_dictionary.items():
            primary_node_bool = Class.primary_node

            node_max_transcode_workers = (
                Class.transcode_max_cpu + Class.transcode_max_gpu
            )

            priority_number = Class.priority

            if priority_number > highest_priority_number:
                highest_priority_transcode_workers = node_max_transcode_workers
                highest_priority_transcode_workers = priority_number

            if primary_node_bool:
                if Class.online:
                    is_primary_alive = True
                else:
                    is_primary_alive = False

                primary_node_transcode_workers = node_max_transcode_workers

                if Class.shutdown_command is None:
                    is_primary_killable = False
                else:
                    is_primary_killable = True

            else:
                max_transcode_workers += node_max_transcode_workers

        quantity_of_nodes = len(node_dictionary)
        quantity_of_nodes_minus_primary = quantity_of_nodes - 1

        if max_nodes > quantity_of_nodes:
            if is_primary_alive:
                if max_nodes > quantity_of_nodes_minus_primary:
                    print("ERROR: more than one node over max")
                elif max_nodes == quantity_of_nodes_minus_primary:
                    if is_primary_killable:
                        print("ERROR: Not yet implemented")
                        # TODO Consider implementing functionality for killable primary node
                    else:
                        max_transcode_workers -= highest_priority_transcode_workers
                        max_transcode_workers += primary_node_transcode_workers
                        includes_primary_node=True
                else:
                    print(
                        "WARN: POSSIBLE ERROR, unaccounted for possibility in find_quantity_of_transcode_workers function in general_logic.py"
                    )
            else:
                includes_primary_node=False

        return max_transcode_workers,includes_primary_node
