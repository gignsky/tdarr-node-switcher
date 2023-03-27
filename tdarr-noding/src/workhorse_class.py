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
                        self.Configuration, self.node_dictionary
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
                        self.Configuration, self.node_dictionary, node
                    )
                    # set node status to offline
                    self.node_dictionary[node_dict_name].line_state("Offline")

                    # set node directive to sleep
                    self.Status.NodeStatusMaster.update_directive(node, "Sleeping")

        self.update_classes()
        # primary_node = self.Server.primary_node
        # primary_node_class = self.node_dictionary[primary_node]

    #         if primary_node_class.online:
    #             print(f"Primary NODE: `{primary_node}` is ONLINE")
    #             # TODO CHECK FOR ACTIVE WORK ON OTHER ONLINE NODES THEN PAUSE UNTIL EMPTY BEFORE SHUTTING DOWN AFTER RECHECK
    #
    #             number_of_working_nodes = len(nodes_with_work_list)
    #
    #             if number_of_working_nodes == 1:
    #                 print("PLACEHOLDER")
    #                 if quantity_of_living_nodes > 1:
    #                     print("INFO: Shutting/Pausing down all nodes except primary")
    #                     # TODO shutdown all online nodes except primary
    #                 else:
    #                     self.refresh()
    #             else:
    #                 # TODO Same function as above on line 59 looping
    #                 print("PLACEHOLDER")

    def refresh(self):
        Logic.refresh_all(self.Server)

    def normal(self):
        """
        normal run normal workflow when startup has already been run

        all of these steps will function on a "if previous step fails, do not continue" order
        steps to take:
            1. Check for nodes that are going down and see if they have work, if they do not kill these nodes, if and only if this check passes continue with the process if not end the loop and allow for rerunning
            2. Find quantity of work to be done and activate the appropriate number of nodes (while checking to make sure not to go over the max_nodes amount)
            2.5 find that quantity of work is less than required nodes and kill excess nodes
            3. if all work is finished check for online status of primary node, if it is offline attempt to start, if started set all other nodes to zero workers then set workers to normal limits and run refresh
            4. after refresh is complete shutdown primary node if possible and reset regular nodes to workers then rerun function to determine proper number of nodes to be running
        """

        # update nodes
        self.update_nodes()

        # start loop
        q = 1

        while q != 4:
            if q == 1:
                # 1
                # 1.a - find nodes "going down"
                list_of_nodes_going_down = []
                list_of_nodes_going_down_still = []
                for (
                    node,
                    Class,
                ) in self.Status.NodeStatusMaster.node_status_dictionary.items():
                    if Class.directive == "Going_down":
                        list_of_nodes_going_down.append(node)

                # 1.b - find nodes with active work
                _, nodes_without_work_list = tdarr.Tdarr_Logic.find_nodes_with_work(
                    self.Server
                )

                # 1.c - check if nodes going down have no work & shutdown if found to be true
                for node in list_of_nodes_going_down:
                    # ensure workers are set to zero
                    tdarr.Tdarr_Orders.reset_workers_to_zero(
                        self.Server, node, self.node_dictionary
                    )

                    if node in nodes_without_work_list:

                        # order shutdown
                        node_interactions.HostLogic.kill_node(
                            self.Configuration, self.node_dictionary, node
                        )

                        # set node status to offline
                        self.node_dictionary[node].line_state("Offline")

                        # set node directive to sleep
                        self.Status.NodeStatusMaster.update_directive(node, "Sleeping")

                    else:
                        # set node directive to going_down
                        self.Status.NodeStatusMaster.update_directive(
                            node, "Going_down"
                        )
                        list_of_nodes_going_down_still.append(node)

                if len(list_of_nodes_going_down_still) == 0:
                    q += 1
                else:
                    break

                self.update_classes()

            elif q == 2:
                # 2
                # 2.a - find quantity of work to be done
                queued_transcode_ids = tdarr.Tdarr_Logic.search_for_queued_transcodes(
                    self.Server
                )
                queued_transcode_quantity = len(queued_transcode_ids)

                # 2.b - find total amount of work able to be done by all transcode nodes at once
                (
                    max_quantity_of_work,
                    includes_primary_node,
                ) = Logic.find_quantity_of_transcode_workers(
                    self.node_dictionary, self.Server.max_nodes
                )

                # 2.c - compare quantity of work to be done with able to be done, should set var with priority level capable of taking on the load

                # 2.d - activate nodes to priority level if required

                # 2.5a - deactivate nodes to priority level if required

                # 2.5b - deal with incrementing of breaking from q loop, should only increment if all work is done

            elif q == 3:
                print("PLACEHOLDER")
                # 3 - should only run once all work is done
                # 3.a - find primary node name

                # 3.b - check if primary node is online

                # 3.c - if node is offline attempt to start

                # 3.c.1 - if node is started or is already running, set workers to normal amounts

                # 3.c.2 - if node is started or is already running, set all other online nodes to zero workers and goind_down

                # 3.d - order refresh

                # 3.e - check if all refresh work is done

                # 3.f - deal with incrementing of breaking a q loop, should only increment if all of the refresh is done

            elif q == 4:
                print("PLACEHOLDER")
                # 4 - should only run after the end of a refresh
                # 4.a - attempt shutdown of primary node if possible
                # 4.a.1 - set workers on primary node to zero

                # 4.a.2 - attempt shutdown of primary node

                # 4.b - increment q to 5 and end the loop all work is done
                q = 5
