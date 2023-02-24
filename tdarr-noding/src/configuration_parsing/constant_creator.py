from . import Server, Node


class Constants_Setup:
    """
        class to setup constants for server and node
    < Document Guardian | Protect >
    """

    def __init__(self, configuration_file):
        """
        __init__ setup basic configuration file information

        Args:
            configuration_file (pyyaml to json): configuration file brought in to json from pyyaml import

        < Document Guardian | Protect >
        """
        self.configuration_file = configuration_file

        self.program_folder_path = configuration_file["program"]["folder_path"]

    def setup_server_class(self):
        """
        setup_server_class configures server class and returns it

        < Document Guardian | Protect >
        """
        server_inner_dictionary = self.configuration_file["tdarr_server"]
        self.Server = Server(server_inner_dictionary)

        return self.Server

    def setup_node_class(self, get_nodes_output):
        """
        setup_node_class setup node classes and return dictionary of said classes with names in the keys

        Args:
            get_nodes_output (json): json from tdarr/get_nodes endpoint

        Returns:
            dictionary: dictionary of nodes classes with keys being the name of the node
        < Document Guardian | Protect >
        """
        config_node_inner_dictionary = self.configuration_file["tdarr_nodes"]

        # get nodes from yaml config
        self.node_dictionary = Server.expected_nodes_creator(
            Server, config_node_inner_dictionary
        )

        # get nodes from tdarr and compare
        get_nodes_output_keys = list(get_nodes_output.keys())
        get_nodes_output_names = []
        preexisting_node_dictionary_keys = list(self.node_dictionary.keys())

        ## make list of node names from get_nodes output
        for get_node_id in get_nodes_output_keys:
            keys_dictionary = get_nodes_output[get_node_id]
            name = keys_dictionary["nodeName"]
            get_nodes_output_names.append(name)

        ## search for expected and unexpected nodes from tdarr get_nodes with online and offline setting
        for get_node_name in get_nodes_output_names:
            if get_node_name in preexisting_node_dictionary_keys:
                self.node_dictionary[get_node_name].line_state("Online")
                for node_id in get_nodes_output:
                    node_id_inner_dictionary = get_nodes_output[node_id]
                self.node_dictionary[get_node_name].update_with_tdarr_dictionary(
                    node_id_inner_dictionary, "Expected"
                )
            else:
                new_node_class = Node(get_node_name, None, "Unexpected")
                new_node_class.line_state("Online")
                for node_id in get_nodes_output:
                    node_id_inner_dictionary = get_nodes_output[get_node_id]
                new_node_class.update_with_tdarr_dictionary(
                    node_id_inner_dictionary, "Unexpected"
                )
                self.node_dictionary[get_node_name] = new_node_class

        ##check for dead nodes
        for node_name in self.node_dictionary:
            node_class = self.node_dictionary[node_name]
            if node_class.online is None:
                node_class.line_state("Offline")

        return self.node_dictionary
