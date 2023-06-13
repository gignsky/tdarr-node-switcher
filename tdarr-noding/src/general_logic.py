import requests
import yaml
from pathlib import Path
from . import tdarr
from . import node_interactions
import time


class Logic:
    @staticmethod
    def refresh_all(constants, refresh_type=None):
        """
        refresh_all health checks and transcodes

        Args:
            constants (_type_): _description_
        """
        print("Refreshing...")
        tdarr.Tdarr_Orders.refresh_health_checks(constants)
        tdarr.Tdarr_Orders.update_transcodes(constants, refresh_type)

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
                # highest_priority_transcode_workers_priority_number = priority_number

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
                    #! LOOK AT ME AT SOME POINT
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
            for _, Class in node_dictionary.items():
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

        if includes_primary_node:
            priority_array = priority_array_with_primary
        else:
            priority_array = priority_array_without_primary

        cumulative_quantity = 0
        for priority_level, quantity in priority_array.items():
            if queued_quantity <= quantity:
                target_priority = priority_level
                break
            elif queued_quantity >= quantity:
                cumulative_quantity += quantity
                if queued_quantity <= cumulative_quantity:
                    target_priority = priority_level
                    break
                else:
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

    @staticmethod
    def primary_node_just_started(
        Server, node_dictionary, primary_node_name, Status, Configuration, Workhorse
    ):
        """
        primary_node_just_started does things that should be done after a node starts for primary node

        Args:
            Server (Class): basic server class
            node_dictionary (dict): dict of names and their associated classes
            primary_node_name (str): node name
        < Document Guardian | Protect >
        """
        print("INFO: Updating nodes")
        Workhorse.update_nodes()
        # reset node workers to none
        tdarr.Tdarr_Orders.reset_workers_to_zero(
            Server, primary_node_name, node_dictionary
        )

        # sleep for time to update
        print("INFO: Sleeping for 5 seconds to allow nodes to update")
        time.sleep(5)

        print("INFO: Updating nodes")
        Workhorse.update_nodes()
        # set workers to max
        tdarr.Tdarr_Orders.reset_workers_to_max_limits(
            Server, primary_node_name, node_dictionary
        )

        # 4.f.2 - if node is started or is already running, set all other online nodes to zero workers and goind_down
        list_of_living_nodes_excluding_primary = []
        for node, Class in node_dictionary.items():
            if not Class.primary_node:
                if Class.online:
                    ###4.f.2.a - append online nodes to list of living nodes if not the primary node
                    list_of_living_nodes_excluding_primary.append(node)

        ##4.f.2.d - shutdown nodes if no work
        ####4.f.2.d.1 - deactivate nodes to priority level if required
        list_of_nodes_still_going_down = []
        for node in list_of_living_nodes_excluding_primary:
            # mark as going down
            Status.NodeStatusMaster.update_directive(node, "Going_down")

            # set workers to zero
            tdarr.Tdarr_Orders.reset_workers_to_zero(Server, node, node_dictionary)

            # check if work exists on node - if it does pass this option until no work exists then shutdown
            ## check get list of nodes with work
            (
                nodes_with_work_list,
                _,
            ) = tdarr.Tdarr_Logic.find_nodes_with_work(Server)

            if node not in nodes_with_work_list:
                node_interactions.HostLogic.kill_node(
                    Configuration,
                    node_dictionary,
                    node,
                    Status,
                )
            else:
                list_of_nodes_still_going_down.append(node)

        return list_of_nodes_still_going_down
