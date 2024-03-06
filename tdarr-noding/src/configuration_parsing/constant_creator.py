from . import Server, Node


class ConstantsSetup:
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
        self.ansible_folder_path = configuration_file["program"]["ansible_path"]
        self.cache_folder_path = configuration_file["program"]["cache_path"]

        self.Server = None

        self.expected_nodes_dictionary = None

    def setup_server_class(self):
        """
        setup_server_class configures server class and returns it

        < Document Guardian | Protect >
        """
        server_inner_dictionary = self.configuration_file["tdarr_server"]
        self.Server = Server(server_inner_dictionary)

        return self.Server

    def setup_node_class(
        self, get_nodes_output
    ):  # Ignoring error with unused "get_nodes_output"
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
        self.expected_nodes_dictionary = Server.expected_nodes_creator(
            Server, config_node_inner_dictionary
        )

        return self.expected_nodes_dictionary

    def update_node_class_with_tdarr(self, get_nodes_output):
        """
        update_node_class_with_tdarr updates node classes with tdarr's get_node_output text by searching for online vs offline and expectedness in the configuration file

        Args:
            get_nodes_output (json dict): json dict output of the tdarr get_nodes_output function

        Returns:
            dict: a dictionary of node names and their associated classes
        < Document Guardian | Protect >
        """
        # get nodes from tdarr and compare
        get_nodes_output_keys = list(get_nodes_output.keys())
        get_nodes_output_names = []
        preexisting_node_dictionary_keys = list(self.expected_nodes_dictionary.keys())

        ## make list of node names from get_nodes output
        for get_node_id in get_nodes_output_keys:
            keys_dictionary = get_nodes_output[get_node_id]
            name = keys_dictionary["nodeName"]
            get_nodes_output_names.append(name)

        ## search for expected and unexpected nodes from tdarr get_nodes with online and offline setting
        for get_node_name in get_nodes_output_names:
            if get_node_name in preexisting_node_dictionary_keys:
                self.expected_nodes_dictionary[get_node_name].line_state("Online")
                for node_id in get_nodes_output:
                    node_id_inner_dictionary = get_nodes_output[node_id]
                    node_name = node_id_inner_dictionary["nodeName"]
                    if (
                        node_name
                        == self.expected_nodes_dictionary[get_node_name].node_name
                    ):
                        self.expected_nodes_dictionary[
                            get_node_name
                        ].update_with_tdarr_dictionary(
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
                self.expected_nodes_dictionary[get_node_name] = new_node_class

        ##check for dead nodes
        for node_name, node_class in self.expected_nodes_dictionary.items():
            if node_class.online is None:
                node_class.line_state("Offline")

        ## update current transcode limits
        self.update_current_transcode_worker_amounts(
            self.expected_nodes_dictionary, get_nodes_output
        )

        return self.expected_nodes_dictionary

    def update_current_transcode_worker_amounts(
        self, node_dictionary, get_nodes_output
    ):
        """
        update_current_transcode_worker_amounts update's node classes with most current information from get_nodes_output

        Args:
            node_dictionary (dict): dict of node names and their associated classes
            get_nodes_output (json dict): json dict response of the get_nodes_output function
        < Document Guardian | Protect >
        """
        for node_id in get_nodes_output:
            inner_node_dictionary = get_nodes_output[node_id]
            node_name = inner_node_dictionary["nodeName"]
            worker_limits_dictionary = inner_node_dictionary["workerLimits"]

            node_class = node_dictionary[node_name]

            # Find current node worker limits
            current_cpu_transcode = worker_limits_dictionary["transcodecpu"]
            current_gpu_transcode = worker_limits_dictionary["transcodegpu"]
            current_cpu_healthcheck = worker_limits_dictionary["healthcheckcpu"]
            current_gpu_healthcheck = worker_limits_dictionary["healthcheckgpu"]

            # set node_class current worker limits
            node_class.set_current_worker_levels(
                current_cpu_transcode,
                current_gpu_transcode,
                current_cpu_healthcheck,
                current_gpu_healthcheck,
            )
