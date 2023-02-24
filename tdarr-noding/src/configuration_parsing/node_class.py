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

    def expected_or_not(self, expected_or_not):
        if expected_or_not == "Expected":
            self.expected = True
            print(f"INFO: FROM NODE CLASS: `{self.node_name}` is Expected")
        elif expected_or_not == "Unexpected":
            self.expected = False
            print(f"WARN: FROM NODE CLASS: `{self.node_name}` is Unexpected")

    def set_healthcheck_limits(self):
        """
        set_healthcheck_limits sets worker limits based of yaml config
        < Document Guardian | Protect >
        """

    def set_transcode_limits(self):
        """
        set_transcode_limits sets worker limits based of yaml config
        < Document Guardian | Protect >
        """

    def update_with_tdarr_dictionary(
        self, tdarr_node_inner_id_dictionary, expected_or_not
    ):
        self.id_string = tdarr_node_inner_id_dictionary["_id"]
        self.expected_or_not(expected_or_not)
        self.tdarr_node_inner_dictionary = tdarr_node_inner_id_dictionary

        """
        expected_or_not sets self.expected to either true or false based on inputted string

        Args:
            expected_or_not (string): "Expected" or "Unexpected"
        < Document Guardian | Protect >
        """
