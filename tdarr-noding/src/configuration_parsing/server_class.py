from . import Node


class Server:
    def __init__(self, server_inner_dict):
        self.server_inner_dict = server_inner_dict

        # configure default server information
        self.default_server_configuration()

    # node class list creator
    def expected_nodes_creator(self, node_dictionary):
        """
        expected_nodes_creator gathers expected nodes from config yaml file and creates node classes in a dictionary to return

        Args:
            node_dictionary (dictionary): keys are names of nodes, values are node classes
        """
        for name in node_dictionary:
            node_inner_dictionary = node_dictionary[name]
            self.expected_nodes_dictionary[name] = Node(
                name, node_inner_dictionary, "Expected"
            )

    # configure default server information
    def default_server_configuration(self):
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


#     def determine_tdarr_nodes(self, node_inner_dictionary):
#         self.list_of_tdarr_nodes = {}
#
#         for id_string in node_inner_dictionary:
#             sub_inner_id_dictionary = node_inner_dictionary[id_string]
#             name = sub_inner_id_dictionary["nodeName"]
#             self.list_of_tdarr_nodes[name] = sub_inner_id_dictionary
