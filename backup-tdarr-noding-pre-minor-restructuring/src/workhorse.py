from . import configuration_parsing
from . import Logic
from . import tdarr
from . import node_interactions


class Workhorse:
    """
    general workhorse for the entireprogram where the large amount of overall processing is handled

    < Document Guardian | Protect >
    """

    # setup constants
    def setup_constants(self, configuration_file):
        """
        setup_constants configures the constants class and returns that class as well as server class and a dictionary with keys being the node names and value being node's class

        Args:
            configuration_file (yaml to json): configuration file from root directory after converted to json via the yaml import

        Returns:
            Classes: Constants, Server, (dictionary of classes) node_dictionary

        < Document Guardian | Protect >
        """
        self.Constants = configuration_parsing.ConstantsSetup(configuration_file)

        # setup server
        self.Server = self.Constants.setup_server_class()

        # setup nodes
        get_nodes_output = tdarr.Tdarr_Logic.generic_get_nodes(self.Server)
        self.node_dictionary = self.Constants.setup_node_class(get_nodes_output)

        #reset nodes to zero workers
        for node in self.node_dictionary:
            node_class = self.node_dictionary[node]
            # set primary node
            if node_class.primary_node:
                self.Server.add_primary_node(node)

        # setup status check
        self.script_status_file = Logic.script_status(self.Constants)

        return self.Server, self.node_dictionary, self.script_status_file

    # main methods
    def refresh(self):
        Logic.refresh_all(self.Constants)

    def normal(self):
        if self.script_status_file == "Stopped":
            self.startup()
        else:
            print("PLACEHOLDER")
            # TODO Write info in for reading yaml status file and the rest of what to do after startup has finished executing

    def startup(self):
        """
        startup function: this will run at the inital start of the script when no status file exists
        < Document Guardian | Protect >
        """
        # initiate start up

        # find quantity of online nodes
        quantity_of_living_nodes = 0
        current_priority_level = 0
        for node in self.node_dictionary:
            node_class = self.node_dictionary[node]
            line_state = node_class.online
            priority_level = node_class.priority
            if line_state:
                quantity_of_living_nodes += 1
                if priority_level >= current_priority_level:
                    current_priority_level = priority_level
            #reset nodes to zero workers
            tdarr.Tdarr_Logic.reset_workers_to_zero(self.Server,self.node_dictionary)

        if quantity_of_living_nodes > self.Server.max_nodes:
            print(
                "WARNING: Too many nodes alive; killing last node on the priority list"
            )
            node_interactions.HostLogic.kill_smallest_priority_node(self.Constants,self.node_dictionary)
            # TODO write script to shutdown single worst priority node

        primary_node = self.Server.primary_node
        primary_node_class = self.node_dictionary[primary_node]

        if primary_node_class.online:
            print(f"Primary NODE: `{primary_node}` is ONLINE")
            # TODO CHECK FOR ACTIVE WORK ON OTHER ONLINE NODES THEN PAUSE UNTIL EMPTY BEFORE SHUTTING DOWN AFTER RECHECK
            nodes_with_work_list = tdarr.Tdarr_Logic.find_nodes_with_work(
                self.Constants
            )

            number_of_working_nodes = len(nodes_with_work_list)

            if number_of_working_nodes == 1:
                print("PLACEHOLDER")
                if quantity_of_living_nodes > 1:
                    print("INFO: Shutting/Pausing down all nodes except primary")
                    # TODO shutdown all online nodes except primary
                else:
                    self.refresh()
            else:
                # TODO Same function as above on line 59 looping
                print("PLACEHOLDER")