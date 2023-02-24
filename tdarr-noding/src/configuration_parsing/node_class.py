class Node:
    """
    class for individual nodes
    < Document Guardian | Protect >
    """

    def __init__(self, node_name, config_node_inner_dictionary, expected_or_not):
        """
        __init__ basic node setup

        Args:
            node_name (string): name of node in english
            config_node_inner_dictionary (json dictionary): pyyaml conversion to json dictionary from config yaml
            expected_or_not (string): dictates whether or not node was expected in the config yaml file
        < Document Guardian | Protect >
        """
        self.node_name = node_name
        self.config_node_inner_dictionary = config_node_inner_dictionary

        if config_node_inner_dictionary is not None:
            self.priority = self.config_node_inner_dictionary["priority"]
            try:
                self.primary_node = bool(config_node_inner_dictionary["primary_node"])
            except KeyError:
                self.primary_node = False

            # setup max and mins
            self.set_healthcheck_limits()
            self.set_transcode_limits()

        else:
            self.primary_node = False

        self.online = None
        self.expected = None

        # expected determination
        self.expected_or_not(expected_or_not)

    def line_state(self, online_or_offline):
        """
        line_state sets the node class to online or offline

        Args:
            online_or_offline (string): "Online" or "Offline" setting the state of this nodes bool
        """
        if online_or_offline == "Online":
            self.online = True
            print(f"INFO: FROM NODE CLASS: `{self.node_name}` is Online")
        elif online_or_offline == "Offline":
            print(f"INFO: FROM NODE CLASS: `{self.node_name}` is Offline")
            self.online = False

    # def set_current_worker_levels(self):
    #     self.current_cpu_transcode = "PLACEHOLDER"
    #     self.current_gpu_transcode = "PLACEHOLDER"
    #     self.current_cpu_healthcheck = "PLACEHOLDER"
    #     self.current_gpu_healthcheck = "PLACEHOLDER"

    def set_healthcheck_limits(self):
        """
        set_healthcheck_limits sets worker limits based of yaml config
        < Document Guardian | Protect >
        """
        if self.config_node_inner_dictionary is not None:
            self.healthcheck_min_cpu = self.config_node_inner_dictionary[
                "healthcheck_worker_limits"
            ]["min_cpu"]
            self.healthcheck_max_cpu = self.config_node_inner_dictionary[
                "healthcheck_worker_limits"
            ]["max_cpu"]
            self.healthcheck_min_gpu = self.config_node_inner_dictionary[
                "healthcheck_worker_limits"
            ]["min_gpu"]
            self.healthcheck_max_gpu = self.config_node_inner_dictionary[
                "healthcheck_worker_limits"
            ]["max_gpu"]
        else:
            self.healthcheck_min_cpu = None
            self.healthcheck_max_cpu = None
            self.healthcheck_min_gpu = None
            self.healthcheck_max_gpu = None

    def set_transcode_limits(self):
        """
        set_transcode_limits sets worker limits based of yaml config
        < Document Guardian | Protect >
        """
        if self.config_node_inner_dictionary is not None:
            self.transcode_min_cpu = self.config_node_inner_dictionary[
                "transcode_worker_limits"
            ]["min_cpu"]
            self.transcode_max_cpu = self.config_node_inner_dictionary[
                "transcode_worker_limits"
            ]["max_cpu"]
            self.transcode_min_gpu = self.config_node_inner_dictionary[
                "transcode_worker_limits"
            ]["min_gpu"]
            self.transcode_max_gpu = self.config_node_inner_dictionary[
                "transcode_worker_limits"
            ]["max_gpu"]
        else:
            self.transcode_min_cpu = None
            self.transcode_max_cpu = None
            self.transcode_min_gpu = None
            self.transcode_max_gpu = None

    def update_with_tdarr_dictionary(
        self, tdarr_node_inner_id_dictionary, expected_or_not
    ):
        """
        update_with_tdarr_dictionary include tdarr inner dictionary inside nodes class

        Args:
            tdarr_node_inner_id_dictionary (dictionary): json dictionary from generic_get_nodes function
            expected_or_not (string): "Expected" or "Unexpected"
        < Document Guardian | Protect >
        """
        self.id_string = tdarr_node_inner_id_dictionary["_id"]
        self.expected_or_not(expected_or_not)
        self.tdarr_node_inner_dictionary = tdarr_node_inner_id_dictionary

    def expected_or_not(self, expected_or_not):
        """
        expected_or_not sets self.expected to either true or false based on inputted string

        Args:
            expected_or_not (string): "Expected" or "Unexpected"
        < Document Guardian | Protect >
        """
        if expected_or_not == "Expected":
            self.expected = True
            print(f"INFO: FROM NODE CLASS: `{self.node_name}` is Expected")
        elif expected_or_not == "Unexpected":
            self.expected = False
            print(f"WARN: FROM NODE CLASS: `{self.node_name}` is Unexpected")
