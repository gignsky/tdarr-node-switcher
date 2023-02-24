from . import Node


class Server:
    """
        class to setup information important to the tdarr server
    < Document Guardian | Protect >
    """

    def __init__(self, server_inner_dict):
        """
        __init__ basic server setup

        Args:
            server_inner_dict (json dictionary from config yaml): configuration yaml config section regarding tdarr_server
        < Document Guardian | Protect >
        """
        self.server_inner_dict = server_inner_dict

        # configure default server information
        self.default_server_configuration()

    # node class list creator
    def expected_nodes_creator(self, node_dictionary):
        """
        expected_nodes_creator gathers expected nodes from config yaml file and creates node classes in a dictionary to return

        Args:
            node_dictionary (dictionary): keys are names of nodes, values are node classes
        < Document Guardian | Protect >
        """
        expected_nodes_dictionary = {}
        for name in node_dictionary:
            node_inner_dictionary = node_dictionary[name]
            expected_nodes_dictionary[name] = Node(
                name, node_inner_dictionary, "Expected"
            )

        return expected_nodes_dictionary

    # configure default server information
    def default_server_configuration(self):
        """
        default_server_configuration default server endpoint configuration
        < Document Guardian | Protect >
        """
        self.set_up_urls()

        self.max_nodes = self.server_inner_dict["max_nodes"]

        self.priority_level = self.server_inner_dict["default_priority_level"]

    def set_up_urls(self):
        url = self.server_inner_dict["url"]
        api_string = self.server_inner_dict["api_string"]

        ######################################
        tdarr_useable_url = f"{url}{api_string}"
        ######################################

        self.get_nodes = f"{tdarr_useable_url}/get-nodes"

        self.status = f"{tdarr_useable_url}/status"

        self.mod_worker_limit = f"{tdarr_useable_url}/alter-worker-limit"

        self.search = f"{tdarr_useable_url}/search-db"

        self.update_url = f"{tdarr_useable_url}/cruddb"
