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

    @staticmethod
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
                highest_priority_transcode_workers_priority_number = priority_number

            if primary_node_bool:
                if Class.online:
                    is_primary_alive = True
                else:
                    is_primary_alive = False

                primary_node_transcode_workers = node_max_transcode_workers

                if Class.shutdown is None:
                    is_primary_killable = False
                else:
                    is_primary_killable = True

            else:
                max_transcode_workers += node_max_transcode_workers

        quantity_of_nodes = len(node_dictionary)
        quantity_of_nodes_minus_primary = quantity_of_nodes - 1

        if quantity_of_nodes > max_nodes:
            if is_primary_alive:
                if quantity_of_nodes_minus_primary > max_nodes:
                    print("ERROR: more than one node over max")
                elif max_nodes == quantity_of_nodes_minus_primary:
                    if is_primary_killable:
                        print("ERROR: Not yet implemented")
                        # TODO Consider implementing functionality for killable primary node
                    else:
                        max_transcode_workers -= highest_priority_transcode_workers
                        max_transcode_workers += primary_node_transcode_workers
                else:
                    print(
                        "WARN: POSSIBLE ERROR, unaccounted for possibility in find_quantity_of_transcode_workers function in general_logic.py"
                    )

        if is_primary_alive:
            includes_primary_node = True
        else:
            includes_primary_node = False

        return max_transcode_workers, includes_primary_node

    @staticmethod
    def find_priority_target_level(
        queued_quantity,
        max_transcode_workers,
        includes_primary_node,
        node_dictionary,
        max_nodes,
    ):

        # create two arrays with priority number and total transcode workers
        priority_array_without_primary = {}
        priority_array_with_primary = {}
        cap = max_nodes

        if includes_primary_node:
            cap -= 1

        current_priority_level = 0
        while current_priority_level <= cap:
            for node, Class in node_dictionary.items():
                node_priority = Class.priority
                node_transcode_workers = (
                    Class.transcode_max_cpu + Class.transcode_max_gpu
                )
                if node_priority == current_priority_level:
                    if node_priority == 0:
                        priority_array_with_primary[
                            node_priority
                        ] = node_transcode_workers
                        current_priority_level += 1
                        break
                    else:
                        if includes_primary_node:
                            priority_array_with_primary[
                                node_priority
                            ] = node_transcode_workers
                        else:
                            priority_array_without_primary[
                                node_priority
                            ] = node_transcode_workers
                        current_priority_level += 1
                        break
                elif node_priority == cap:
                    current_priority_level += 1
                    break

        if includes_primary_node:
            priority_array = priority_array_with_primary
        else:
            priority_array = priority_array_without_primary

        cumulative_quantity = 0
        for priority_level, quantity in priority_array.items():
            if queued_quantity <= quantity:
                target_priority = priority_level
            elif queued_quantity >= quantity:
                cumulative_quantity += quantity
                target_priority = priority_level

        return target_priority

    #
    #         for _,Class in node_dictionary.items():
    #             priority_level=Class.transcode_max_cpu + Class.transcode_max_gpu
    #
    #
    #         if includes_primary_node:
    #             primary_node_workers=0
    #             priority_level=0
    #             for _, Class in node_dictionary.items():
    #                 if Class.primary:
    #                     primary_node_workers+=Class.transcode_max_cpu + Class.transcode_max_gpu
    #             for priority_level in range(max_nodes):
    #                 for _, Class in node_dictionary.items():
    #                     if priority_level == Class.priority_level:

    @staticmethod
    def activate_node_to_priority_level(node_dictionary, priority_target):
        nodes_to_activate = []
        for node, Class in node_dictionary.items():
            if Class.priority <= priority_target:
                if not Class.online:
                    nodes_to_activate.append(node)

        return nodes_to_activate

    @staticmethod
    def deactivate_node_to_priority_level(node_dictionary, priority_target):
        nodes_to_deactivate = []
        for node, Class in node_dictionary.items():
            if Class.priority > priority_target:
                if Class.online:
                    nodes_to_deactivate.append(node)

        return nodes_to_deactivate
