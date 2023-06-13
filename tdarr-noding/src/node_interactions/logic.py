from . import HostCommands


class HostLogic:
    @staticmethod
    def kill_smallest_priority_node(configuration_class, node_dictionary, Status):
        """
        kill_smallest_priority_node kills the node with the highest priority number

        Args:
            node_dictionary (dict): keys are node names values are assoicated classes
        < Document Guardian | Protect >
        """
        high_priority_node_name = HostLogic.get_node_with_highest_priority(
            node_dictionary
        )
        HostLogic.kill_node(
            configuration_class, node_dictionary, high_priority_node_name, Status
        )

        return high_priority_node_name

    @staticmethod
    def get_node_with_highest_priority(node_dictionary):
        """
        get_node_with_highest_priority find name of node with the highest priority number and therefor the one that should be shutdown first

        Args:
            node_dictionary (dict): dict of node names and their associated classes

        Returns:
            str: node name for highest priority node
        < Document Guardian | Protect >
        """
        max_priority_level = 0
        max_priority_online_node_name = ""
        for node_name in node_dictionary:
            if node_dictionary[node_name].online:
                current_priority = node_dictionary[node_name].priority
                if current_priority > max_priority_level:
                    max_priority_level = current_priority
                    max_priority_online_node_name = node_name

        return max_priority_online_node_name

    @staticmethod
    def kill_node(configuration_class, node_dictionary, name, Status):
        """
        kill_node does the stuff to nicely shutdown a node

        Args:
            configuration_class (Class): basic configuration class
            node_dictionary (dict): dict of node names and thier associated classes
            name (str): node name string
            Status (Class): basic status class
        < Document Guardian | Protect >
        """
        for node in node_dictionary:
            if name == node:
                if node_dictionary[node].online:
                    # print to console
                    print(f"Killing Node: '{name}'")

                    # find shutdown command
                    shutdown_command = node_dictionary[node].shutdown

                    # order shutdown
                    HostCommands.shutdown_node(configuration_class, shutdown_command)

                    # change status to sleeping and offline
                    ##change status to sleeping
                    Status.NodeStatusMaster.node_status_dictionary[
                        name
                    ].update_directive("Sleeping")

                    ##change state to offline
                    node_dictionary[node].line_state("Offline")

    @staticmethod
    def start_node(configuration_class, node_dictionary, name, Status):
        """
        start_node does the stuff to nicely startup a node

        Args:
            configuration_class (Class): basic config class
            node_dictionary (dict): dict of node names and their associated classes
            name (str): node name to act upon
            Status (Class): basic status class
        < Document Guardian | Protect >
        """
        for node in node_dictionary:
            if name == node:
                if not node_dictionary[node].online:
                    # print to console
                    print(f"Starting Node: '{name}'")

                    # find startup command
                    startup_command = node_dictionary[node].startup

                    # order startup
                    did_i_fail = HostCommands.startup_node(
                        configuration_class, startup_command
                    )

                    if not did_i_fail:
                        # change status to active and online
                        ##change status to active
                        Status.NodeStatusMaster.node_status_dictionary[
                            name
                        ].update_directive("Active")

                        ##change state to online
                        node_dictionary[node].line_state("Online")
