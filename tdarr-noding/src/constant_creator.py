class Constants:
    def __init__(self, configuration):
        tdarr_url = configuration["tdarr_server"]["url"]
        api_string = configuration["tdarr_server"]["api_string"]

        self.program_folder_path = configuration["program"]["folder_path"]
        self.max_nodes = configuration["tdarr_server"]["max_nodes"]
        self.set_up_urls(tdarr_url, api_string)
        self.setup_list_of_node_names(configuration)

    def set_up_urls(self, TDARR_URL, api_string):
        ######################################
        self.TDARR_USEABLE_URL = f"{TDARR_URL}{api_string}"
        ######################################

        self.GET_NODES = f"{self.TDARR_USEABLE_URL}/get-nodes"

        self.STATUS = f"{self.TDARR_USEABLE_URL}/status"

        self.MOD_WORKER_LIMIT = f"{self.TDARR_USEABLE_URL}/alter-worker-limit"

        self.SEARCH = f"{self.TDARR_USEABLE_URL}/search-db"

        self.UPDATE_URL = f"{self.TDARR_USEABLE_URL}/cruddb"

    def setup_list_of_node_names(self, configuration):
        tdarr_nodes_dictionary = configuration["tdarr_nodes"]

        self.list_of_tdarr_node_names = []
        self.list_of_tdarr_node_inner_dicts = []

        for name in tdarr_nodes_dictionary:
            self.list_of_tdarr_node_names.append(name)
            self.list_of_tdarr_node_inner_dicts.append(
                tdarr_nodes_dictionary[f"{name}"]
            )

        self.set_primary_node(configuration)

    def set_primary_node(self, configuration):
        for name, dict in zip(
            self.list_of_tdarr_node_names, self.list_of_tdarr_node_inner_dicts
        ):
            if "primary_node" in dict:
                if dict["primary_node"] == True:
                    self.primary_node_name = name
