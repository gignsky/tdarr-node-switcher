class Node:
    def __init__(self, node_name, config_node_inner_dictionary, expected_or_not):
        self.node_name = node_name
        self.config_node_inner_dictionary = config_node_inner_dictionary

        self.priority = self.config_node_inner_dictionary["priority"]
        try:
            self.primary_node = bool(config_node_inner_dictionary["primary_node"])
        except KeyError:
            self.primary_node = False

        self.online = None
        self.expected = None
        # expected determination
        self.expected_or_not(expected_or_not)

        # setup max and mins
        self.set_healthcheck_limits()
        self.set_transcode_limits()

    def line_state(self, online_or_offline):
        if online_or_offline == "Online":
            self.online = True
            print(f"INFO: `{self.node_name}` is Online")
        elif online_or_offline == "Offline":
            print(f"INFO: `{self.node_name}` is Offline")
            self.online = False

    def expected_or_not(self, expected_or_not):
        if expected_or_not == "Expected":
            self.expected = True
            print(f"INFO: `{self.node_name}` is Expected")
        elif expected_or_not == "Unexpected":
            self.expected = False
            print(f"WARN: `{self.node_name}` is Unexpected")

    def set_healthcheck_limits(self):
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

    def set_transcode_limits(self):
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

    def update_with_tdarr_dictionary(
        self, tdarr_node_inner_id_dictionary, expected_or_not
    ):
        self.id_string = tdarr_node_inner_id_dictionary["_id"]
        self.expected_or_not(expected_or_not)
        self.tdarr_node_inner_dictionary = tdarr_node_inner_id_dictionary

    def set_current_worker_levels(self):
        self.current_cpu_transcode = "PLACEHOLDER"
        self.current_gpu_transcode = "PLACEHOLDER"
        self.current_cpu_healthcheck = "PLACEHOLDER"
        self.current_gpu_healthcheck = "PLACEHOLDER"
