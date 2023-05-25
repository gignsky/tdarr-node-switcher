from . import Configuration as ConfigurationClass
from . import StatusTracking
from . import tdarr
from . import node_interactions
from . import Logic


class Workhorse:
    """
    general workhorse for the entireprogram where the large amount of overall processing is handled

    < Document Guardian | Protect >
    """

    # main methods
    def __init__(self, current_directory):
        """
        __init__ setup classes to be used each time the program runs

        Args:
            current_directory (str): path to current working directory of main.py

        < Document Guardian | Protect >
        """
        print("SECTION INFO: Starting workhorse '__init__'")
        self.root_dir = current_directory
        self.Configuration = ConfigurationClass(self.root_dir)

        self.Server = self.Configuration.setup_server_class()

        # check if configuration file exists
        (
            self.status_exists,
            self.status_file,
        ) = self.Configuration.check_if_status_exists()

        self.Status = StatusTracking(self.status_file, self.Configuration.STATUS_PATH)

        self.node_dictionary = self.Configuration.setup_configuration_node_dictionary()

        # set primary node name in node class
        for node, Class in self.node_dictionary.items():
            if Class.primary_node:
                self.Server.add_primary_node(node)

    def update_nodes_output(self):
        """
        update_nodes_output updates self.get_nodes_output to most current pull from tdarr server
        < Document Guardian | Protect >
        """
        self.get_nodes_output = tdarr.Tdarr_Logic.generic_get_nodes(self.Server)

    def update_classes(self):
        """
        update_classes update classes with current information
        < Document Guardian | Protect >
        """
        print("SECTION INFO: Starting workhorse 'UPDATE_CLASSES'")
        # refresh get_nodes_output
        self.update_nodes()

        # update node master
        # refresh status class & print output
        self.Status.status_update(self.node_dictionary)

    def update_nodes(self):
        """
        update_nodes General update nodes
        < Document Guardian | Protect >
        """
        self.update_nodes_output()

        # refresh tdarr node classes
        list_of_alive_tdarr_nodes = []

        for node_id in self.get_nodes_output:
            inner_tdarr_dictionary = self.get_nodes_output[node_id]
            node_name = inner_tdarr_dictionary["nodeName"]
            list_of_alive_tdarr_nodes.append(node_name)

        for name, Class in self.node_dictionary.items():
            # run update in node class
            if name in list_of_alive_tdarr_nodes:
                for node_id in self.get_nodes_output:
                    inner_tdarr_dictionary = self.get_nodes_output[node_id]
                    inner_tdarr_dictionary_name = inner_tdarr_dictionary["nodeName"]
                    if inner_tdarr_dictionary_name == name:
                        Class.update_node("Online", inner_tdarr_dictionary)
            else:
                Class.update_node("Offline")

    def refresh(self):
        Logic.refresh_all(self.Server)

    def startup(self):
        """
        startup function: this will run at the inital start of the script when no status file exists

            The purpose of this function is to reset the nodes and server to a known point in order to begin noding.

            steps to be taken in this function:
            1. get inital tdarr get_nodes output and update the classes with relevant information
            2. ensure that all nodes are set to zero workers
            3. ensure that more than the max nodes number is not running at once, and if found to be true shutdown nodes with smallest priority
            4. kill nodes without active work
            5. run workhorse update function to update config with most current information
        < Document Guardian | Protect >
        """
        # initiate start up - and configure node master initally
        self.Status.startup_configure_node_master(self.node_dictionary)

        ## 1
        ### 1.a get_nodes output
        self.update_nodes_output()

        ### 1.b update configuration class with tdarr info
        self.Configuration.startup_update_nodes_with_tdarr_info(
            self.node_dictionary, self.get_nodes_output
        )

        ## 2
        for node_name, node_class in self.node_dictionary.items():
            if node_class.online:
                tdarr.Tdarr_Orders.reset_workers_to_zero(
                    self.Server, node_name, self.node_dictionary
                )

        ## 3
        quantity_of_living_nodes = 999  # set quantity of living nodes to an absurdly high number to allow for looping on next section

        ### 3.a - begin looping to kill lowest priority nodes
        while quantity_of_living_nodes > self.Server.max_nodes:
            quantity_of_living_nodes = Logic.find_quant_living_nodes(
                self.node_dictionary
            )

            if quantity_of_living_nodes > self.Server.max_nodes:
                print(
                    "WARNING: Too many nodes alive; killing last node on the priority list"
                )
                highest_priority_node_name = (
                    node_interactions.HostLogic.kill_smallest_priority_node(
                        self.Configuration, self.node_dictionary, self.Status
                    )
                )

                # decrement quantity of living nodes
                quantity_of_living_nodes -= 1
                # set node state to offline
                self.node_dictionary[highest_priority_node_name].line_state("Offline")

        # commented out for new system of work
        # Logic.reset_node_workers(self.Server,self.node_dictionary)

        ## 4
        _, nodes_without_work_list = tdarr.Tdarr_Logic.find_nodes_with_work(self.Server)

        # shutdown nodes without work
        for node in nodes_without_work_list:
            for node_dict_name in self.node_dictionary:
                if node == node_dict_name:
                    # set workers to zero
                    tdarr.Tdarr_Orders.reset_workers_to_zero(
                        self.Server, node, self.node_dictionary
                    )
                    # order shutdown
                    node_interactions.HostLogic.kill_node(
                        self.Configuration, self.node_dictionary, node, self.Status
                    )
                    # set node status to offline
                    self.node_dictionary[node_dict_name].line_state("Offline")

                    # set node directive to sleep
                    self.Status.NodeStatusMaster.update_directive(node, "Sleeping")

        self.update_classes()
        # primary_node = self.Server.primary_node
        # primary_node_class = self.node_dictionary[primary_node]

        self.normal()

    def normal(self):
        """
        normal running NEW workflow for concise operations

        steps to take:
            1. Check for the following
                1.a. nodes going down
                1.b. nodes with and without work
                1.c. quantity of work to be done and to be able to be done
                1.d. check if primary node is online
            2. Calculate if nodes need to be activated or deactivated
                2.a. find current priority level
                2.b. gather list of nodes to be activated and deactivated
            3. Activate or deactivate nodes
                3.a. deactivate nodes
                3.b. activate nodes
            4. Ensure all nodes are at correct worker count
                4.a. update values
                    4.a.1. update list_of_nodes_going_down
                    4.a.2. update or create list of living nodes
                4.b. update worker count
                    4.b.1. skip nodes going down
                    4.b.2. update worker counts on all living nodes
            5. Check if all work is finished
        """

        # initalize NormalHelpers class
        NormalHelpers = NormalHelpers(self.Server, self.Status, self.node_dictionary)

        # update nodes
        print("INFO: Updating nodes...")
        self.update_nodes()

        print("INFO: Gathering General Information...")

        # 1.a
        # find list of nodes going down
        list_of_nodes_going_down = []
        for (
            node,
            Class,
        ) in self.Status.NodeStatusMaster.node_status_dictionary.items():
            if Class.directive == "Going_down":
                list_of_nodes_going_down.append(node)

        print(
            f"The following nodes are already marked as 'going_down' {list_of_nodes_going_down}"
        )

        # 1.b
        # find nodes with current work
        (
            nodes_without_work_list,
            nodes_with_work_list,
        ) = tdarr.Tdarr_Logic.find_nodes_with_work(self.Server)

        print(f"The following nodes have work: {nodes_with_work_list}")
        print(f"The following nodes do NOT have work: {nodes_without_work_list}")

        # 1.c
        # find quantity of work
        (
            quantity_of_work,
            max_quantity_of_work,
            max_quantity_includes_primary,
        ) = NormalHelpers.find_quantity_of_work()

        print(f"Quantity of work: {quantity_of_work}")
        print(f"Max quantity of work: {max_quantity_of_work}")
        print(
            f"Max quantity of work includes primary node: {max_quantity_includes_primary}"
        )

        # 1.d
        # check if primary node is online
        primary_node = self.Server.primary_node

        print(f"Primary node: {primary_node}")

        # 2
        # calculate if nodes need to be activated or deactivated

        # 2.a
        # find current priority level
        current_priority_level = NormalHelpers.find_current_priority_level()

        print(f"Current Running Priority Level: {current_priority_level}")

        # 2.b
        # gather list of nodes to be activated and deactivated
        (
            nodes_to_activate,
            nodes_to_deactivate,
        ) = NormalHelpers.calculate_nodes_to_activate_deactivate()

        print(f"Nodes to be activated: {nodes_to_activate}")
        print(f"Nodes to be deactivated: {nodes_to_deactivate}")

        # 3
        # activate or deactivate nodes

        # 3.a
        # deactivate nodes
        if len(nodes_to_deactivate) > 0:
            for node in nodes_to_deactivate:
                print("INFO: Deactivating node: {node}")

                if node in list_of_nodes_going_down:
                    if node in nodes_without_work_list:
                        print(
                            f"INFO: {node} is already marked as 'Going_down' and has completed its work. Shutting down node..."
                        )
                        NormalHelpers.shutdown_node(node)
                    else:
                        print(
                            f"INFO: {node} is already marked as 'Going_down'. Waiting for node to complete work..."
                        )
                else:
                    # set directive to going_down
                    NormalHelpers.set_node_going_down(node, nodes_without_work_list)

        # 3.b
        # activate nodes
        if len(nodes_to_activate) > 0:
            for node in nodes_to_activate:
                print(f"INFO: Activating node: {node}")
                NormalHelpers.activate_node(node)

        # 4
        # ensure all nodes are at correct worker count

        # 4.a
        # update values

        # 4.a.1
        # update list_of_nodes_going_down
        list_of_nodes_going_down = []
        for (
            node,
            Class,
        ) in self.Status.NodeStatusMaster.node_status_dictionary.items():
            if Class.directive == "Going_down":
                list_of_nodes_going_down.append(node)

        # 4.a.2
        # update or create list of living nodes
        list_of_living_nodes = []
        for node, Class in self.node_dictionary.items():
            if Class.status == "Online":
                list_of_living_nodes.append(node)

        # 4.b
        # update worker count

        for node in list_of_living_nodes:
            # 4.b.1
            # skip nodes going down
            if node in list_of_nodes_going_down:
                print(
                    f"INFO: {node} is marked as 'Going_down'. Skipping Worker Count Update..."
                )

            # 4.b.2
            # update worker counts on all living nodes
            else:
                print(f"INFO: Checking worker count on: {node}...")

                # reset worker count to worker limit
                tdarr.Tdarr_Orders.reset_workers_to_max_limits(
                    self.Server, node, self.node_dictionary
                )

                print(f"INFO: Worker count on {node} has been updated.")

        # 5
        # check if all work is finished

        if quantity_of_work == 0:
            print(
                "INFO: All work is finished. Shutting down all nodes except primary..."
            )
            for node in list_of_living_nodes:
                if node != primary_node:
                    NormalHelpers.shutdown_node(node)

            # update status to Normal_Finished
            self.Status.change_state("Normal_Finished")

            # 5.a
            # check if primary node is online & continue to post Normal


#         q = 1
#
#         while q != 7:
#             print(f"INFO: Starting Q{q}")
#             if q == 1:
#                 # 1
#                 print("Starting Q1: Checking for nodes going down")
#                 # 1.a - find nodes "going down"
#                 list_of_nodes_going_down = []
#                 list_of_nodes_going_down_still = []
#                 for (
#                     node,
#                     Class,
#                 ) in self.Status.NodeStatusMaster.node_status_dictionary.items():
#                     if Class.directive == "Going_down":
#                         list_of_nodes_going_down.append(node)
#                         print(f"INFO: {node} is already marked as 'Going_down'")
#
#                 # 1.b - find nodes with active work
#                 print("INFO: Finding nodes without work")
#                 _, nodes_without_work_list = tdarr.Tdarr_Logic.find_nodes_with_work(
#                     self.Server
#                 )
#                 for node in nodes_without_work_list:
#                     print(f"INFO: The following nodes has no work: {node}")
#
#                 # 1.c - check if nodes going down have no work & shutdown if found to be true
#                 for node in list_of_nodes_going_down:
#                     # ensure workers are set to zero
#                     tdarr.Tdarr_Orders.reset_workers_to_zero(
#                         self.Server, node, self.node_dictionary
#                     )
#
#                     if node in nodes_without_work_list:
#                         # order shutdown
#                         node_interactions.HostLogic.kill_node(
#                             self.Configuration, self.node_dictionary, node, self.Status
#                         )
#
#                         # set node status to offline
#                         self.node_dictionary[node].line_state("Offline")
#
#                         # set node directive to sleep
#                         self.Status.NodeStatusMaster.update_directive(node, "Sleeping")
#
#                     else:
#                         # set node directive to going_down
#                         self.Status.NodeStatusMaster.update_directive(
#                             node, "Going_down"
#                         )
#                         list_of_nodes_going_down_still.append(node)
#
#                 if len(list_of_nodes_going_down_still) == 0:
#                     q += 1
#                     # self.Status.change_state(f"Normal_q{q}")
#                 else:
#                     print("INFO: Updating classes...")
#                     # q += 1  #* TEMPORARY FIX MIGHT NEED TO BE REMOVED - removed by commented out
#                     self.update_classes()
#                     break  # * TEMPORARY FIX MIGHT NEED TO BE REMOVED - THESE CHANGES BYPASS SAFTEYS - removed by uncommenting
#
#                 print("INFO: Updating classes...")
#                 self.update_classes()
#
#             elif q == 2:
#                 # 2
#                 # 2.a - find quantity of work to be done
#                 print("INFO: Finding list and quantity of queued work")
#                 queued_transcode_ids = tdarr.Tdarr_Logic.search_for_queued_transcodes(
#                     self.Server
#                 )
#                 queued_transcode_quantity = len(queued_transcode_ids)
#                 print(f"INFO: Quantity of Queued Work: {queued_transcode_quantity}")
#
#                 # 2.b - find total amount of work able to be done by all transcode nodes at once
#                 (
#                     max_quantity_of_work,
#                     includes_primary_node,
#                 ) = Logic.find_quantity_of_transcode_workers(
#                     self.node_dictionary, self.Server.max_nodes
#                 )
#
#                 print(
#                     f"INFO: Max Quantity of Work able to be done: {max_quantity_of_work}"
#                 )
#                 print(
#                     f"INFO: Primary Node is included in above statement: {includes_primary_node}"
#                 )
#
#                 # 2.c - compare quantity of work to be done with able to be done, should set var with priority level capable of taking on the load
#                 priority_level_target = Logic.find_priority_target_level(
#                     queued_transcode_quantity,
#                     max_quantity_of_work,
#                     includes_primary_node,
#                     self.node_dictionary,
#                     self.Server.max_nodes,
#                 )
#                 print(f"INFO: priority level target = {priority_level_target}")
#                 # 2.d - get list of nodes to deactivate
#                 list_of_nodes_to_deactivate = Logic.deactivate_node_to_priority_level(
#                     self.node_dictionary, priority_level_target
#                 )
#
#                 print(
#                     f"INFO: List of nodes to deactivate: {list_of_nodes_to_deactivate}"
#                 )
#
#                 # 2.e - deactivate nodes to priority level if required
#                 for node in list_of_nodes_to_deactivate:
#                     print(f"INFO: Deactivating node: {node}")
#                     # mark as going down
#                     self.Status.NodeStatusMaster.update_directive(node, "Going_down")
#
#                     # set workers to zero
#                     tdarr.Tdarr_Orders.reset_workers_to_zero(
#                         self.Server, node, self.node_dictionary
#                     )
#
#                     # check if work exists on node - if it does pass this option until no work exists then shutdown
#                     ## check get list of nodes with work
#                     nodes_with_work_list, _ = tdarr.Tdarr_Logic.find_nodes_with_work(
#                         self.Server
#                     )
#
#                     if node not in nodes_with_work_list:
#                         node_interactions.HostLogic.kill_node(
#                             self.Configuration, self.node_dictionary, node, self.Status
#                         )
#
#                 # 2.5.a - get list of nodes to activate to priority level if required
#                 list_of_nodes_to_activate = Logic.activate_node_to_priority_level(
#                     self.node_dictionary, priority_level_target
#                 )
#                 print("list_of_nodes_to_activate = " + f"{list_of_nodes_to_activate}")
#
#                 # 2.5.b - activate and setup their class stuff
#                 for node in list_of_nodes_to_activate:
#                     # activate
#                     node_interactions.HostLogic.start_node(
#                         self.Configuration, self.node_dictionary, node, self.Status
#                     )
#
#                     ###### commented out for normal level activation later on
#                     # # set workers to normal levels
#                     # for node_name, Class in self.node_dictionary:
#                     #     if node == node_name:
#                     #         dict_of_max_levels = Class.max_level_dict_creator()
#                     #         for worker_type, max_level in dict_of_max_levels.items():
#                     #             tdarr.Tdarr_Orders.set_worker_level(
#                     #                 self.Server, Class, max_level, worker_type
#                     #             )
#
#                 # 2.5c - deal with incrementing of breaking from q loop, should only increment if all work is done
#                 print("INFO: Updating classes")
#                 self.update_classes()
#                 continue_to_q3 = True
#                 for (
#                     node,
#                     Class,
#                 ) in self.Status.NodeStatusMaster.node_status_dictionary.items():
#                     if Class.directive == "Going_down":
#                         # break  #* TEMPOARY FIX MIGHT NEED TO BE REMOVED - removed by commenting out
#                         continue_to_q3 = False
#
#                 if continue_to_q3:
#                     q += 1
#                     # self.Status.change_state(f"Normal_q{q}")
#
#             elif q == 3:
#                 # 3 - should set active nodes to max worker levels #* in the future consider limiting this amount to smaller numbers in the case of less than max work level being what is required
#                 # 3.a - loop over nodes to find list of alive nodes
#                 list_of_alive_nodes = []
#                 for node, Class in self.node_dictionary.items():
#                     if Class.online:
#                         list_of_alive_nodes.append(node)
#                 print(f"INFO: List of living nodes: {list_of_alive_nodes}")
#
#                 # 3.b - loop over list of alive nodes and set worker levels to normal
#                 for name in list_of_alive_nodes:
#                     tdarr.Tdarr_Orders.reset_workers_to_max_limits(
#                         self.Server, name, self.node_dictionary
#                     )
#
#                 q += 1
#                 self.Status.change_state(f"Normal_q{q}")
#
#             elif q == 4:
#                 # 4 - should only run once all work is done
#                 # 4.a - find quantity of work to be done
#                 print("INFO: Finding list and quantity of queued work")
#                 queued_transcode_ids = tdarr.Tdarr_Logic.search_for_queued_transcodes(
#                     self.Server
#                 )
#                 queued_transcode_quantity = len(queued_transcode_ids)
#                 print(f"INFO: Quantity of Queued Work: {queued_transcode_quantity}")
#
#                 if queued_transcode_quantity == 0:
#                     # 4.b find primary node name
#                     primary_node = self.Server.primary_node
#
#                     # 4.d - check if primary node is online
#                     if self.node_dictionary[primary_node].online:
#                         primary_online = True
#                     else:
#                         primary_online = False
#
#                     # 4.e - if node is offline attempt to start
#                     if not primary_online:
#                         startup_command = self.node_dictionary[primary_node].startup
#                         if startup_command is not None:
#                             node_interactions.HostLogic.start_node(
#                                 self.Configuration,
#                                 self.node_dictionary,
#                                 primary_node,
#                                 self.Status,
#                             )
#                             Logic.primary_node_just_started(
#                                 self.Server,
#                                 self.node_dictionary,
#                                 primary_node,
#                                 self.Status,
#                                 self.Configuration,
#                                 self,
#                             )
#                         else:
#                             print(
#                                 f"WARN: No Startup Command for Priamry Node '{primary_node}'"
#                             )
#                             tdarr.Tdarr_Orders.update_transcodes(
#                                 self.Server, True
#                             )  # * Don't know if this line even works, added in without testing as a fix for refreshing successful transcodes when primary node is offline
#                             break
#                     # 4.f.1 - if node is started or is already running, set workers to normal amounts
#                     else:
#                         list_of_nodes_still_going_down = (
#                             Logic.primary_node_just_started(
#                                 self.Server,
#                                 self.node_dictionary,
#                                 primary_node,
#                                 self.Status,
#                                 self.Configuration,
#                                 self,
#                             )
#                         )
#
#                     if len(list_of_nodes_still_going_down) == 0:
#                         if primary_online:
#                             # 4.g - order refresh - and increment
#                             self.refresh()
#                             q += 1
#                             # self.Status.change_state(f"Normal_q{q}")
#                         else:
#                             self.Status.change_state("Started")
#                             break
#                 else:
#                     break
#             elif q == 5:
#                 # 5.a - check if all refresh work is done
#                 queued_transcode_ids = tdarr.Tdarr_Logic.search_for_queued_transcodes(
#                     self.Server
#                 )
#                 queued_transcode_quantity = len(queued_transcode_ids)
#                 print(f"INFO: Quantity of Queued Work: {queued_transcode_quantity}")
#
#                 refresh_finished = False
#
#                 if queued_transcode_quantity == 0:
#                     refresh_finished = True
#
#                 # 5.b - deal with incrementing of breaking a q loop, should only increment if all of the refresh is done
#                 if refresh_finished:
#                     q += 1
#                     # self.Status.change_state(f"Normal_q{q}")
#
#             elif q == 6:
#                 print("PLACEHOLDER")
#                 # 6 - should only run after the end of a refresh
#                 # 6.a - attempt shutdown of primary node if possible
#                 # 6.a.1 - set workers on primary node to zero
#
#                 # 6.a.2 - attempt shutdown of primary node
#
#                 # 6.b - increment q to 5 and end the loop all work is done


class NormalHelpers:
    """
    logic extracted from the normal function for cleanlyness's sake
    """

    def __init__(self, Server, Status, Configuration, node_dictionary):
        self.Server = Server
        self.Status = Status
        self.Configuration = Configuration
        self.node_dictionary = node_dictionary

    def work_quantity_finder(self):
        """
        work_quantity_finder find quantity of work to be done and max quantity of work able to be done by all transcode nodes at once

        Returns:
            queued_transcode_quantity (int): int value of quantity of queued work
            max_quantity_of_work (int): int value of max quantity of work able to be done by all transcode nodes at once
            includes_primary_node (bool): bool value of whether or not the max_quantity_of_work includes the primary node
        < Document Guardian | Protect >
        """
        # 2
        # 2.a - find quantity of work to be done
        print("INFO: Finding list and quantity of queued work")
        queued_transcode_ids = tdarr.Tdarr_Logic.search_for_queued_transcodes(
            self.Server
        )
        queued_transcode_quantity = len(queued_transcode_ids)
        print(f"INFO: Quantity of Queued Work: {queued_transcode_quantity}")

        # 2.b - find total amount of work able to be done by all transcode nodes at once
        (
            max_quantity_of_work,
            includes_primary_node,
        ) = Logic.find_quantity_of_transcode_workers(
            self.node_dictionary, self.Server.max_nodes
        )

        return queued_transcode_quantity, max_quantity_of_work, includes_primary_node

    def find_current_priority_level(self):
        """
        find_current_priority_level find priority level of online nodes

        Returns:
            current_priority_level (int): int value of current priority level of online nodes
        < Document Guardian | Protect >
        """

        # find list of online node names
        online_node_names = []
        for node_name in self.node_dictionary:
            if self.node_dictionary[node_name].online:
                online_node_names.append(node_name)

        # find current priority level
        current_priority_level = 0
        for node_name in online_node_names:
            if self.node_dictionary[node_name].priority_level > current_priority_level:
                current_priority_level = self.node_dictionary[node_name].priority_level

        return current_priority_level

    def calculate_nodes_to_activate_deactivate(
        self, queued_transcode_quantity, max_quantity_of_work, includes_primary_node
    ):
        """
        calculate_nodes_to_activate_deactivate

        Args:
            queued_transcode_quantity (int): quantity of queued work
            max_quantity_of_work (int): max quantity of work able to be done by all transcode nodes at once
            includes_primary_node (bool): bool value of whether or not the max_quantity_of_work includes the primary node

        Returns:
            list_of_nodes_to_activate (list): list of node names to activate
            list_of_nodes_to_deactivate (list): list of node names to deactivate
        < Document Guardian | Protect >
        """

        priority_level_target = Logic.find_priority_target_level(
            queued_transcode_quantity,
            max_quantity_of_work,
            includes_primary_node,
            self.node_dictionary,
            self.Server.max_nodes,
        )

        print(f"INFO: Priority Level Target: {priority_level_target}")

        # find list of nodes to activate/deactivate
        list_of_nodes_to_deactivate = Logic.deactivate_node_to_priority_level(
            self.node_dictionary, priority_level_target
        )

        list_of_nodes_to_activate = Logic.activate_node_to_priority_level(
            self.node_dictionary, priority_level_target
        )

        return list_of_nodes_to_activate, list_of_nodes_to_deactivate

    def set_node_going_down(self, node, nodes_without_work_list):
        """
        set_node_going_down set node to going down

        Args:
            node (str): name of node
            nodes_without_work_list (list): list of nodes without work
        < Document Guardian | Protect >
        """
        self.Status.NodeStatusMaster.update_directive(node, "Going_down")

        # set workers to zero
        tdarr.Tdarr_Orders.reset_workers_to_zero(
            self.Server, node, self.node_dictionary
        )

        # check if node has no work
        if node in nodes_without_work_list:
            # order shutdown
            self.shutdown_node(node)

    def shutdown_node(self, node):
        """
        shutdown_node shuts node down gracefully

        Args:
            node (str): node name
        < Document Guardian | Protect >
        """
        node_interactions.HostLogic.kill_node(
            self.Configuration, self.node_dictionary, node, self.Status
        )
        # set node status to offline
        self.node_dictionary[node].line_state("Offline")

        # set node directive to sleep
        self.Status.NodeStatusMaster.update_directive(node, "Sleeping")

    def activate_node(self, node):
        """
        activate_node

        Args:
            node (str): node name
        < Document Guardian | Protect >
        """
        node_interactions.HostLogic.start_node(
            self.Configuration, self.node_dictionary, node, self.Status
        )
        # set node status to online
        self.node_dictionary[node].line_state("Online")

        # set node directive to normal
        self.Status.NodeStatusMaster.update_directive(node, "Normal")
