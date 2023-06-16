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
            try:
                self.priority = self.config_node_inner_dictionary["priority"]
            except KeyError:
                self.priority = None

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
        self.startup = None
        self.shutdown = None

        # expected determination
        self.expected_or_not(expected_or_not)

        self.find_startup_shutdown_cmd()

    def find_startup_shutdown_cmd(self):
        """
        find_startup_shutdown_cmd extracts startup shell statements from the config file
            for each individual node; these were written in ansible in the original implementation.

        < Document Guardian | Protect >
        """
        try:
            startup_command = self.config_node_inner_dictionary["startup_command"]
        except KeyError:
            startup_command = None
        try:
            shutdown_command = self.config_node_inner_dictionary["shutdown_command"]
        except KeyError:
            shutdown_command = None

        # fix up startup and shutdown
        if startup_command is not None:
            startup_command = startup_command.split()
        if shutdown_command is not None:
            shutdown_command = shutdown_command.split()

        # print(f"Startup CMD:{startup_command}")
        # print(f"Shutdown CMD:{shutdown_command}")
        self.startup = startup_command
        self.shutdown = shutdown_command

    def update_node(self, line_state, tdarr_inner_dictionary=None):
        """
        update_node updates a node with more current information

        Args:
            line_state (str): "Online" or "Offline" (Status of Node)
            tdarr_inner_dictionary (json dict, optional): json dict section of the tdarr get_nodes_output. Defaults to None.
        < Document Guardian | Protect >
        """
        self.line_state(line_state)
        self.update_with_tdarr_dictionary(tdarr_inner_dictionary, "Expected")

        # update current workers amounts
        if tdarr_inner_dictionary is not None:
            worker_limits_dictionary = tdarr_inner_dictionary["workerLimits"]

            current_cpu_transcode = worker_limits_dictionary["transcodecpu"]
            current_gpu_transcode = worker_limits_dictionary["transcodegpu"]
            current_cpu_healthcheck = worker_limits_dictionary["healthcheckcpu"]
            current_gpu_healthcheck = worker_limits_dictionary["healthcheckgpu"]

            self.set_current_worker_levels(
                current_cpu_transcode,
                current_gpu_transcode,
                current_cpu_healthcheck,
                current_gpu_healthcheck,
            )

    def line_state(self, online_or_offline):
        """
        line_state sets the node class to online or offline

        Args:
            online_or_offline (string): "Online" or "Offline" setting the state of this nodes bool
        < Document Guardian | Protect >
        """
        if online_or_offline == "Online":
            self.online = True
            # print(f"INFO: FROM NODE CLASS: `{self.node_name}` is Online")
        elif online_or_offline == "Offline":
            # print(f"INFO: FROM NODE CLASS: `{self.node_name}` is Offline")
            self.online = False

    def set_current_worker_levels(
        self,
        current_cpu_transcode,
        current_gpu_transcode,
        current_cpu_healthcheck,
        current_gpu_healthcheck,
    ):
        """
        set_current_worker_levels set each worker type's current level in a specific instance of the node class

        Args:
            current_cpu_transcode (int): integer value of current_cpu_transcode
            current_gpu_transcode (int): integer value of current_gpu_transcode
            current_cpu_healthcheck (int): integer value of current_cpu_healthcheck
            current_gpu_healthcheck (int): integer value of current_gpu_healthcheck
        < Document Guardian | Protect >
        """
        self.current_cpu_transcode = current_cpu_transcode
        self.current_gpu_transcode = current_gpu_transcode
        self.current_cpu_healthcheck = current_cpu_healthcheck
        self.current_gpu_healthcheck = current_gpu_healthcheck

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
        self.tdarr_node_inner_dictionary = tdarr_node_inner_id_dictionary

        # added block to deal with None being inputted for tdarr_node_inner_id_dictionary
        if self.tdarr_node_inner_dictionary is not None:
            self.id_string = self.tdarr_node_inner_dictionary["_id"]
        else:
            self.id_string = None

        self.expected_or_not(expected_or_not)

    def expected_or_not(self, expected_or_not):
        """
        expected_or_not sets self.expected to either true or false based on inputted string

        Args:
            expected_or_not (string): "Expected" or "Unexpected"
        < Document Guardian | Protect >
        """
        if expected_or_not == "Expected":
            self.expected = True
            # print(f"INFO: FROM NODE CLASS: `{self.node_name}` is Expected")
        elif expected_or_not == "Unexpected":
            self.expected = False
            # print(f"WARN: FROM NODE CLASS: `{self.node_name}` is Unexpected")
