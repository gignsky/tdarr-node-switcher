"""
    Basic class for reading configuration file and reading the saved status version from last run
    < Document Guardian | Protect >
"""
import yaml
from . import configuration_parsing as config_setup_folder
from . import tdarr
from . import Logic

class Configuration:
    """
        Basic class for reading configuration file and reading the saved status version from last run
    < Document Guardian | Protect >
    """

    def __init__(self,tdarr_noding_path):
        """
        setup_constants configures the constants class and returns that class as well as server class and a dictionary with keys being the node names and value being node's class

        Args:
            configuration_file (yaml to json): configuration file from root directory after converted to json via the yaml import

        Returns:
            Classes: Constants, Server, (dictionary of classes) node_dictionary

        < Document Guardian | Protect >
        """

        #constant path for configuration file
        self.CONFIGURATION_PATH=f"{tdarr_noding_path}/tdarr-noding/configuration.yml"
        self.STATUS_PATH=f"{tdarr_noding_path}/tdarr-noding/status.yml"

        #load config file into yaml json dict
        with open(self.CONFIGURATION_PATH, "r") as file:
            self.configuration_file=yaml.safe_load(file)

        self.Constants = config_setup_folder.ConstantsSetup(self.configuration_file)

    def setup_server_class(self):
        # setup server
        self.Server = self.Constants.setup_server_class()

        return self.Server

    def setup_configuration_node_dictionary(self):
        # get nodes output
        get_nodes_output=tdarr.Tdarr_Logic.generic_get_nodes(self.Server)

        # setup nodes
        self.expected_node_dictionary = self.Constants.setup_node_class(get_nodes_output)

        return self.expected_node_dictionary

    def startup_update_nodes_with_tdarr_info(self,node_dictionary,get_nodes_output):
        #set primary node
        for node,node_class in node_dictionary.items():
            # set primary node
            if node_class.primary_node:
                self.Server.add_primary_node(node)

        #update nodes with tdarr info
        self.Constants.update_node_class_with_tdarr(get_nodes_output)

    def check_if_status_exists(self):
        # setup status check
        self.script_status_file = Logic.script_status(self.STATUS_PATH)

        if self.script_status_file == "Empty":
            return False,None
        else:
            with open(self.STATUS_PATH, "r") as file:
                self.status_file=yaml.safe_load(file)

            return True,self.status_file
