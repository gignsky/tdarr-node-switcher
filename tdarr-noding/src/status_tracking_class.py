import yaml


class StatusTracking:
    def __init__(self, status_file, path):
        self.status_dict = {"state": "Initalizing"}
        self.path = path
        if status_file is None:
            self.status_file = None
            self.configure_server_status()
        else:
            self.status_file = status_file
            self.state = status_file["state"]
            self.status_dict["state"] = status_file["state"]

            try:
                self.refreshed_time = status_file["refreshed_time"]
                self.status_dict["refreshed_time"] = status_file["refreshed_time"]
                self.errored_transcodes_quantity = status_file[
                    "errored_transcodes_quantity"
                ]
                self.status_dict[
                    "errored_transcodes_quantity"
                ] = self.errored_transcodes_quantity
            except KeyError:
                self.refreshed_time = None
                self.errored_transcodes_quantity = None

            self.import_server_status()
            self.import_node_status()

    # print output
    def print_status_file(self):
        """
        print_status_file output status file
        < Document Guardian | Protect >
        """
        with open(self.path, "w") as file:
            # server_status_file_output=
            yaml.dump(self.status_dict, file)

    # modify stuff

    def change_state(self, state):
        """
        change_state change state for status tracking

        Args:
            state (str): state
        < Document Guardian | Protect >
        """
        self.state = state
        self.status_dict["state"] = state

    def add_refreshed_time(self, time):
        """
        add_refreshed_time adds time to status file

        Args:
            time (str): time
        < Document Guardian | Protect >
        """
        self.refreshed_time = time
        self.status_dict["refreshed_time"] = time

    def add_number_of_errored_transcodes(self, number):
        self.errored_transcodes_quantity = number
        self.status_dict[
            "errored_transcodes_quantity"
        ] = self.errored_transcodes_quantity

    # importing
    def import_server_status(self):
        """
        import_server_status reads yml file to import server status into status class
        < Document Guardian | Protect >
        """

        status_server_section = self.status_file["tdarr_server"]

        self.ServerStatus = ServerStatus(status_server_section)

    def import_node_status(self):
        """
        import_node_status import status from yaml for nodes
        < Document Guardian | Protect >
        """
        # set up node status dictionary
        if len(self.ServerStatus.tdarr_nodes_status_dictionary) != 0:
            self.NodeStatusMaster = NodeStatusMaster(
                self.ServerStatus.tdarr_nodes_status_dictionary
            )
        else:
            self.NodeStatusMaster = None

    def configure_server_status(self):
        """
        configure_server_status configures server status class when there is no status file as of yet
        < Document Guardian | Protect >
        """
        self.ServerStatus = ServerStatus()
        self.import_node_status()

    def startup_configure_node_master(self, node_dictionary):
        """
        startup_configure_node_master configure nodes master upon startup

        Args:
            node_dictionary (dict): node name and it's associated class
        < Document Guardian | Protect >
        """
        self.NodeStatusMaster = NodeStatusMaster(node_dictionary)

    # updates
    def status_update(self, regular_node_dictionary):
        """
        status_update update status

        Args:
            regular_node_dictionary (dict): node name and it's associated class
        < Document Guardian | Protect >
        """
        # update status dict
        if self.NodeStatusMaster is not None:
            self.ServerStatus.update_server_dict(
                self.NodeStatusMaster.node_status_dictionary, regular_node_dictionary
            )
        self.status_dict["tdarr_server"] = self.ServerStatus.status_dict

        self.print_status_file()


class ServerStatus:
    def __init__(self, status_server_section=None):
        if status_server_section is not None:
            self.state = status_server_section["state"]
            self.status_dict = {}
            self.status_dict["state"] = self.state

            # setup basic node info
            tdarr_nodes_section_dictionary = status_server_section["tdarr_nodes"]

            # initalize var
            self.tdarr_nodes_status_dictionary = {}

            for name in tdarr_nodes_section_dictionary:
                self.tdarr_nodes_status_dictionary[
                    name
                ] = tdarr_nodes_section_dictionary[name]
        else:
            self.state = None
            self.status_dict = {}
            self.tdarr_nodes_status_dictionary = {}

    # modify stuff
    def change_state(self, state):
        """
        change_state change state of server

        Args:
            state (str): "Online" or "Offline"
        < Document Guardian | Protect >
        """
        self.state = state
        self.status_dict["state"] = self.state

    def set_server_status(self, server_status):
        """
        set_server_status set tdarr server status

        Args:
            server_status (str): "Online" or "Offline"
        < Document Guardian | Protect >
        """
        self.status_dict = {"state": server_status}

    # update stuff
    def update_server_dict(self, node_status_dictionary, regular_node_dictionary):
        """
        update_server_dict updates server status with regular node_dictionary

        Args:
            node_status_dictionary (yaml dict): node status dictionary from yaml status file
            regular_node_dictionary (dict): node names and their associated classes
        < Document Guardian | Protect >
        """
        node_status_dict = {}
        for name, Class in node_status_dictionary.items():
            Class.update_status_dict(regular_node_dictionary[name].online)
            node_status_dict[name] = Class.node_status_dict

        self.status_dict["tdarr_nodes"] = node_status_dict


class NodeStatusMaster:
    def __init__(self, tdarr_nodes_status_dictionary):
        self.node_status_dictionary = {}

        for name, inner_dictionary in tdarr_nodes_status_dictionary.items():
            self.node_status_dictionary[name] = NodeStatus(name, inner_dictionary)

    # def update_node_master(self):
    #     # TODO possible placeholder might not need this function
    #     print("PLACEHOLDER")

    def update_directive(self, name, directive):
        """
        update_directive with string

        Args:
            name (str): node name
            directive (str): "Active","Sleeping","Going_down", etc.
        < Document Guardian | Protect >
        """
        for node_name, NodeClass in self.node_status_dictionary.items():
            if name == node_name:
                NodeClass.update_directive(directive)
                print(
                    f"INFO: FROM NODE CLASS: '{name}' directive changed to '{directive}'"
                )


class NodeStatus:
    def __init__(self, name, node_status_section):
        self.name = name
        if isinstance(node_status_section, dict):
            self.node_status_section = node_status_section
            self.state = self.node_status_section["state"]
            self.directive = self.node_status_section["directive"]
        else:
            self.NodeClass = node_status_section
            self.node_status_section = None
            self.update_line_state(self.NodeClass.online)
            self.directive = "Initalizing"

            self.check_for_sleeping()

    def check_for_sleeping(self):
        """
        check_for_sleeping check if node is sleeping based on it's line state
        < Document Guardian | Protect >
        """
        if self.state == "Online":
            if self.directive != "Going_down":
                self.directive = "Active"
        elif self.state == "Offline":
            self.directive = "Sleeping"

    def update_line_state(self, current_line_state):
        """
        update_line_state update line state with online or offline

        Args:
            current_line_state (str): "Online" or "Offline"
        < Document Guardian | Protect >
        """
        if current_line_state:
            self.state = "Online"
        else:
            self.state = "Offline"

    def update_directive(self, new_directive):
        """
        update_directive update directive with string

        Args:
            new_directive (str): "Active","Going_down","Sleeping", etc.
        < Document Guardian | Protect >
        """
        self.directive = new_directive

    def update_status_dict(self, line_state):
        """
        update_status_dict general update status file

        Args:
            line_state (str): "Online" or "Offline"
        < Document Guardian | Protect >
        """
        self.update_line_state(line_state)
        self.check_for_sleeping()
        self.node_status_dict = {"state": self.state, "directive": self.directive}
