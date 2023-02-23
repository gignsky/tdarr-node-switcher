class Server:
    def __init__(self, server_inner_dict):
        self.server_inner_dict = server_inner_dict

        # configure default server information
        self.default_server_configuration()

    # configure default server information
    def default_server_configuration(self):
        self.set_up_urls()

        self.max_nodes = self.server_inner_dict["max_nodes"]

    def set_up_urls(self):
        url = self.server_inner_dict["url"]
        api_string = self.server_inner_dict["api_string"]

        ######################################
        tdarr_useable_url = f"{tdarr_url}{api_string}"
        ######################################

        self.get_nodes = f"{tdarr_useable_url}/get-nodes"

        self.status = f"{tdarr_useable_url}/status"

        self.mod_worker_limit = f"{tdarr_useable_url}/alter-worker-limit"

        self.search = f"{tdarr_useable_url}/search-db"

        self.update_url = f"{tdarr_useable_url}/cruddb"

    def determine_expected_nodes(self, node_inner_dictionary):
        self.list_of_tdarr_node_names = []
        self.list_of_tdarr_node_inner_dicts = []

        for name in node_inner_dictionary:
            self.list_of_tdarr_node_names.append(name)
            self.list_of_tdarr_node_inner_dicts.append(node_inner_dictionary[f"{name}"])

        self.set_primary_node()

    def set_primary_node(self):
        for name, dict in zip(
            self.list_of_tdarr_node_names, self.list_of_tdarr_node_inner_dicts
        ):
            if "primary_node" in dict:
                if dict["primary_node"] == True:
                    self.primary_node_name = name
