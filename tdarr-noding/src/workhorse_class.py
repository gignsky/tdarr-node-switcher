import time
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
        self.cache_folder_path = self.Configuration.Constants.cache_folder_path

        self.Server = self.Configuration.setup_server_class()

        self.get_nodes_output = tdarr.Tdarr_Logic.generic_get_nodes(self.Server)

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

        # initalize NormalHelpers class
        self.NormalHelpersClass = NormalHelpers(
            self.Server, self.Status, self.Configuration, self.node_dictionary
        )

    def update_nodes_output(self):
        """
        update_nodes_output updates self.get_nodes_output to most current pull from tdarr server
        < Document Guardian | Protect >
        """
        print("SECTION INFO: Starting workhorse 'update_nodes_output'")
        self.get_nodes_output = tdarr.Tdarr_Logic.generic_get_nodes(self.Server)

        self.Configuration.startup_update_nodes_with_tdarr_info(
            self.node_dictionary, self.get_nodes_output
        )

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

        self.Configuration.startup_update_nodes_with_tdarr_info(
            self.node_dictionary, self.get_nodes_output
        )

    def update_nodes(self):
        """
        update_nodes General update nodes
        < Document Guardian | Protect >
        """
        print("SECTION INFO: Starting workhorse 'update_nodes'")
        self.update_nodes_output()

        # refresh tdarr node classes

        list_of_alive_tdarr_nodes = Logic.find_alive_nodes_list(self.get_nodes_output)

        for name, Class in self.node_dictionary.items():
            # run update in node class
            if name in list_of_alive_tdarr_nodes:
                for node_id in self.get_nodes_output:
                    inner_tdarr_dictionary = self.get_nodes_output[node_id]
                    inner_tdarr_dictionary_name = inner_tdarr_dictionary["nodeName"]
                    if inner_tdarr_dictionary_name == name:
                        if Class.just_started:
                            Class.update_node("Online", False, inner_tdarr_dictionary)
                        else:
                            Class.update_node("Online", True, inner_tdarr_dictionary)
            else:
                Class.update_node("Offline", False)

    def refresh(self, refresh_type=None):
        print(f"SECTION INFO: Starting workhorse 'refresh' with type {refresh_type}")
        if refresh_type is None:
            Logic.refresh_all(self.Server)
        elif refresh_type == "succesful":
            Logic.refresh_all(self.Server, True)

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
        print("SECTION INFO: Starting workhorse 'startup'")
        # initiate start up - and configure node master initally
        self.Status.startup_configure_node_master(self.node_dictionary)

        ## 1
        ### 1.a get_nodes output
        self.update_nodes_output()

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

    def verify_primary_running(self):
        """
        verify_primary_running verifies that primary node is running and modifies the status file accordingly
        """

        print("SECTION INFO: Starting workhorse 'verify_primary_running'")

        self.update_classes()

        # check if primary node is running
        primary_node = self.Server.primary_node

        # check if non-primary nodes are running
        online_nodes = []
        for node_name, node_class in self.node_dictionary.items():
            if node_class.online:
                online_nodes.append(node_name)

        # try to pop primary node from online nodes list
        try:
            online_nodes.pop(online_nodes.index(primary_node))
        except ValueError:
            print("VALUE_ERROR: Primary node not online")

        # find nodes with and without work
        nodes_with_work, nodes_without_work = tdarr.Tdarr_Logic.find_nodes_with_work(
            self.Server
        )

        for node_name in online_nodes:
            if node_name in nodes_with_work:
                # set node to going down
                self.Status.NodeStatusMaster.update_directive(node_name, "Going Down")

            elif node_name in nodes_without_work:
                # shutdown node
                # set workers to zero
                tdarr.Tdarr_Orders.reset_workers_to_zero(
                    self.Server, node_name, self.node_dictionary
                )
                # order shutdown
                node_interactions.HostLogic.kill_node(
                    self.Configuration, self.node_dictionary, node_name, self.Status
                )
                # set node status to offline
                self.node_dictionary[node_name].line_state("Offline")

                # set node directive to sleep
                self.Status.NodeStatusMaster.update_directive(node_name, "Sleeping")

        # check if primary node is offline
        if not self.node_dictionary[primary_node].online:
            self.NormalHelpersClass.activate_node(primary_node)

        #             # revert status back to normal
        #             self.Status.change_state("Normal")
        #
        #             # print status again
        #             self.Status.print_status_file()

        # when primary node is online
        # update nodes and check if primary node is online
        self.update_classes()

        if self.node_dictionary[primary_node].online:
            current_errored_transcodes_quantity = (
                self.NormalHelpersClass.number_of_errored_transcodes(self.Server)
            )
            previously_errored_transcode_quantity = (
                self.Status.errored_transcodes_quantity
            )

            if previously_errored_transcode_quantity is not None:
                if (
                    current_errored_transcodes_quantity
                    > previously_errored_transcode_quantity
                ):
                    print("Would REFRESH HERE BUT THIS FUNCTIONALITY IS DISABLED")
            #!TODO Uncomment these lines when the refresh function is implemented
            #                     # Call Refresh
            #                     self.refresh()
            #
            #                     # Set status to refreshed
            #                     self.Status.change_state("Refreshed")
            #
            #                     # print status again
            #                     self.Status.print_status_file()
            #
            #                     self.post_refresh()
            else:
                # check quantity of work
                quantity_of_work, _ = self.NormalHelpersClass.work_quantity_finder()

                # check if quantity of work is greater than zero
                if quantity_of_work > 0:
                    # change status to normal
                    self.Status.change_state("Normal")

                    # print status again
                    self.Status.print_status_file()

                else:
                    # Call Refresh
                    self.refresh()

                    # Set status to refreshed
                    self.Status.change_state("Refreshed")

                    # print status again
                    self.Status.print_status_file()

                    self.post_refresh()

        else:
            # change status to normal
            self.Status.change_state("Normal")

            # print status file again
            self.Status.print_status_file()

    def post_refresh(self):
        print("SECTION INFO: Starting workhorse 'post_refresh'")

        self.update_classes()

        # 1. get quantity of work
        quantity_of_work, _ = self.NormalHelpersClass.work_quantity_finder()

        primary_node = self.Server.primary_node

        # 2. check if quantity of work is greater than zero
        if quantity_of_work > 0:
            # check if primary node is online, if not activate it

            if not self.node_dictionary[primary_node].online:
                self.NormalHelpersClass.activate_node(primary_node)

            print(f"INFO: Quantity of work is {quantity_of_work}")
            print("INFO: Quitting until next instance")
            self.Status.change_state("Refreshed")

        else:
            # refresh succesful transcodes only then check if quantity of work is still zero
            print("INFO: Refresh Complete, refreshing succesful transcodes again")

            self.refresh("succesful")

            quantity_of_work, _ = self.NormalHelpersClass.work_quantity_finder()

            if quantity_of_work == 0:
                print("INFO: Quantity of work is zero, continuing to normal workflow")

                # check if primary node is online if so deactivate it
                if self.node_dictionary[primary_node].online:
                    self.NormalHelpersClass.deactivate_node(primary_node)

                current_time = time.time()
                refreshed_time = self.Status.refreshed_time
                current_errored_transcodes = (
                    self.NormalHelpersClass.number_of_errored_transcodes(self.Server)
                )
                previously_errored_transcodes_quantity = (
                    self.Status.errored_transcodes_quantity
                )

                # check if refreshed time is less then 60 minutes ago
                if refreshed_time is not None:
                    if current_time - refreshed_time < 3600:
                        # do nothing as refresh probobly just finished
                        print(
                            "INFO: Refreshed time is less than 60 minutes ago, doing nothing"
                        )
                    elif (
                        current_errored_transcodes
                        == previously_errored_transcodes_quantity
                    ):
                        # do nothing as errored transcodes are the same as before
                        print(
                            "INFO: Errored transcodes Quantity are the same as before, doing nothing"
                        )
                    else:
                        # change status to normal
                        self.Status.change_state("Normal")
                        print("INFO: Post Refresh Workflow Complete... Quitting...")

                else:
                    self.Status.add_refreshed_time(time.time())

                    number_of_errored_transcodes = (
                        self.NormalHelpersClass.number_of_errored_transcodes(
                            self.Server
                        )
                    )

                    self.Status.add_number_of_errored_transcodes(
                        number_of_errored_transcodes
                    )
                # TODO Look into if this is still neccecary with tdarr's cache functionality, probobly still will be but is more of a 2.0 issue ref #231
                #                 # remove all files in the cache directory
                #                 print("Clearing Cache")
                #                 for filename in os.listdir(self.cache_folder_path):
                #                     file_path = os.path.join(self.cache_folder_path, filename)
                #
                #                     try:
                #                         if os.path.isfile(file_path) or os.path.islink(file_path):
                #                             os.unlink(file_path)
                #                         elif os.path.isdir(file_path):
                #                             shutil.rmtree(file_path)
                #
                #                         print(f"Removed {filename} from Cache")
                #                     except Exception as e:
                #                         print(f"Failed to delete {file_path}. Reason: {e}")

                # print status again
                self.Status.print_status_file()

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
        print("SECTION INFO: Normal Workflow Starting...")

        # update nodes
        self.update_classes()

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
            nodes_with_work_list,
            nodes_without_work_list,
        ) = tdarr.Tdarr_Logic.find_nodes_with_work(self.Server)

        print(f"The following nodes have work: {nodes_with_work_list}")
        print(f"The following nodes do NOT have work: {nodes_without_work_list}")

        # 1.c
        # find quantity of work
        (
            quantity_of_work,
            max_quantity_of_work,
        ) = self.NormalHelpersClass.work_quantity_finder()

        print(f"Quantity of work: {quantity_of_work}")
        print(f"Max quantity of work: {max_quantity_of_work}")

        # 1.d
        # check if primary node is online
        primary_node = self.Server.primary_node

        print(f"Primary node: {primary_node}")

        # 2
        # calculate if nodes need to be activated or deactivated

        # 2.a
        # find current priority level
        current_priority_level = self.NormalHelpersClass.find_current_priority_level()

        print(f"Current Running Priority Level: {current_priority_level}")

        # 2.b
        # gather list of nodes to be activated and deactivated
        (
            nodes_to_activate,
            nodes_to_deactivate,
        ) = self.NormalHelpersClass.calculate_nodes_to_activate_deactivate(
            quantity_of_work, max_quantity_of_work
        )

        print(f"Nodes to be activated: {nodes_to_activate}")
        print(f"Nodes to be deactivated: {nodes_to_deactivate}")

        # 3
        # activate or deactivate nodes

        # 3.a
        # deactivate nodes
        if len(nodes_to_deactivate) > 0:
            for node in nodes_to_deactivate:
                print(f"INFO: Deactivating node: {node}")

                if node in list_of_nodes_going_down:
                    if node in nodes_without_work_list:
                        print(
                            f"INFO: {node} is already marked as 'Going_down' and has completed its work. Shutting down node..."
                        )
                        self.NormalHelpersClass.deactivate_node(node)
                    else:
                        print(
                            f"INFO: {node} is already marked as 'Going_down'. Waiting for node to complete work..."
                        )
                else:
                    # set directive to going_down
                    self.NormalHelpersClass.set_node_going_down(
                        node, nodes_without_work_list
                    )

        # 3.b
        # activate nodes
        if len(nodes_to_activate) > 0:
            for node in nodes_to_activate:
                print(f"INFO: Activating node: {node}")
                self.NormalHelpersClass.activate_node(node)

        # 3.c
        # check if nodes that are "going_down" are actually needed for completion of queued work
        copy_list_of_nodes_going_down = (
            list_of_nodes_going_down  # copied to resolve iteration error
        )

        for node in copy_list_of_nodes_going_down:
            if self.node_dictionary[node].priority <= current_priority_level:
                print(
                    f"INFO: {node} is marked as 'Going_down' but is still needed for queued work. Setting node to 'Active'..."
                )
                self.Status.NodeStatusMaster.update_directive(node, "Active")
                list_of_nodes_going_down.remove(node)

        # 4
        # ensure all nodes are at correct worker count

        # 4.a
        # update values

        # 4.a.0
        # update nodes to check if all nodes that needed to be activated actually got activated.
        self.update_nodes()

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
            if Class.online:
                list_of_living_nodes.append(node)

        list_of_nodes_just_started = []
        for node, Class in self.node_dictionary.items():
            if Class.just_started:
                list_of_nodes_just_started.append(node)
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
            # skip nodes that have just started
            elif node in list_of_nodes_just_started:
                print(f"INFO: {node} has just started. Skipping Worker Count Update...")

            # 4.b.3
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
                    self.NormalHelpersClass.deactivate_node(node)

            # update status to Normal_Finished
            self.Status.change_state("Normal_Finished")

            # print status
            self.Status.print_status_file()

            # 5.a
            # check if primary node is online & continue to post Normal
            self.verify_primary_running()


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
        queued_healthcheck_ids = tdarr.Tdarr_Logic.search_for_queued_healthchecks(
            self.Server
        )
        queued_healthcheck_quantity = len(queued_healthcheck_ids)

        # TODO: This is a temporary fix to ensure that the healthcheck queue is not ignored
        if queued_transcode_quantity == 0:
            if queued_healthcheck_quantity < 5:
                print(
                    f"INFO: Quantity of Healthcheck Queued Work: {queued_healthcheck_quantity}"
                )
                used_quantity = 0
            else:
                used_quantity = queued_healthcheck_quantity
        else:
            used_quantity = max(queued_healthcheck_quantity, queued_transcode_quantity)

        print(f"INFO: Quantity of Queued Work: {used_quantity}")

        # 2.b - find total amount of work able to be done by all transcode nodes at once
        max_quantity_of_work = Logic.find_quantity_of_transcode_workers(
            self.node_dictionary, self.Server.max_nodes
        )

        return used_quantity, max_quantity_of_work

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
            try:
                if self.node_dictionary[node_name].priority > current_priority_level:
                    current_priority_level = self.node_dictionary[node_name].priority
            except TypeError:
                pass

        return current_priority_level

    def calculate_nodes_to_activate_deactivate(
        self, queued_transcode_quantity, max_quantity_of_work
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

        # set nodes to activate to empty if there is no work to be done
        if queued_transcode_quantity == 0:
            list_of_nodes_to_activate = []

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
            self.deactivate_node(node)

    def deactivate_node(self, node):
        """
        shutdown_node shuts node down gracefully

        Args:
            node (str): node name
        < Document Guardian | Protect >
        """
        node_interactions.HostLogic.kill_node(
            self.Configuration, self.node_dictionary, node, self.Status
        )

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

    def number_of_errored_transcodes(self, server):
        # find number of errored transcodes
        returned_item = tdarr.Tdarr_Logic.search_for_failed_transcodes(server)

        number_of_errored_transcodes = len(returned_item)

        return number_of_errored_transcodes
