from . import configuration_parsing
from . import Logic
from . import tdarr


class Workhorse:
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
        Server = self.Constants.setup_server_class()

        # setup nodes
        get_nodes_output = tdarr.Tdarr_Logic.generic_get_nodes(Server)
        node_dictionary = self.Constants.setup_node_class(get_nodes_output)

        return Server, node_dictionary

    # main methods
    def refresh(self):
        Logic.refresh_all(self.Constants)

    def normal(
        self,
    ):
        script_status_file = Logic.script_status(self.Constants)

        if script_status_file == "Stopped":
            self.startup()
        else:
            print("PLACEHOLDER")
            # TODO Write info in for reading yaml status file

    def startup(self):
        # initate start up
        expected_node_status = tdarr.Tdarr_Logic.alive_node_search(self.Constants)
        quantity_of_living_nodes = 0

        for node in expected_node_status:
            print(f"NODE: `{node}` is {expected_node_status[node]}")
            if expected_node_status[node] == "Online":
                quantity_of_living_nodes += 1

        if quantity_of_living_nodes > self.Constants.max_nodes:
            print(
                "WARNING: Too many nodes alive; killing last node on the priority list"
            )
            # TODO write script to shutdown single worst priority node

        primary_node = self.Constants.primary_node_name

        if expected_node_status[primary_node] == "Online":
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
                    refresh(self.Constants)
            else:
                # TODO Same function as above on line 59 looping
                print("PLACEHOLDER")
