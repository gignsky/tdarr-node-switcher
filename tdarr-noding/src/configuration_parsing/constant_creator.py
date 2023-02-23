from . import Server, Node


class Constants_Setup:
    def __init__(self, configuration_file):
        self.configuration_file = configuration_file

        self.program_folder_path = configuration_file["program"]["folder_path"]

        """
        setup_server_class configures server class and returns it

        < Document Guardian | Protect >
        """
        self.Server = Server(server_inner_dictionary)

    def setup_node_class(self):
        config_node_inner_dictionary = self.configuration_file["tdarr_nodes"]
        Server.expected_nodes_creator(Server, config_node_inner_dictionary)
        print(Server.expected_nodes_dictionary)
        # self.Server.set_primary_node()
        # print(Server.primary_node)
        # find additional nodes (unexpected)

    def get_nodes_check(self, get_nodes_dictionary):
        self.all_tdarr_nodes = {}
        for node_id in get_nodes_dictionary:
            node_id_inner_dictionary = get_nodes_dictionary[node_id]
            name = node_id_inner_dictionary["nodeName"]
            self.all_tdarr_nodes[name] = node_id_inner_dictionary

        for expected_node_name in self.Server.expected_nodes_dictionary:
            expected_node_class = self.Server.expected_nodes_dictionary[
                expected_node_name
            ]
            for tdarr_node in self.all_tdarr_nodes:
                if expected_node_name == tdarr_node:
                    expected_node_class.update_with_tdarr_dictionary(
                        self.all_tdarr_nodes[tdarr_node], "Expected"
                    )
                    expected_node_class.line_state("Online")
                # else:
                #     expected_node.update_with_tdarr_dictionary(
                #         self.all_tdarr_nodes[tdarr_node], "Unexpected"
                #     )
            if expected_node_class.online is None:
                expected_node_class.line_state("Offline")


# TODO Reenable the use of notification for unexpected node
#         for tdarr_node in self.all_tdarr_nodes:
#             for expected_node in self.Server.expected_nodes_dictionary:
#                 expected_node_class = self.Server.expected_nodes_dictionary[
#                     expected_node_name
#                 ]
#                 # if expected_node_class.expected is None:
#                 #     expected_node_class.expected_or_not("Unexpected")
#                 #     pass
#
#             print(
#                 f"ERROR: `{tdarr_node}` was NOT Expected and is outside of this programs control"
#             )  # Eventual TODO fix this up so that new nodes can be added and controlled
