class Constants:
    def __init__(self, configuration):
        tdarr_url = configuration["tdarr_server"]["url"]
        api_string = configuration["tdarr_server"]["api_string"]

        self.program_folder_path = configuration["program"]["folder_path"]

        self.set_up_urls(tdarr_url, api_string)

    def set_up_urls(self, TDARR_URL, api_string):
        ######################################
        self.TDARR_USEABLE_URL = f"{TDARR_URL}{api_string}"
        ######################################

        self.GET_NODES = f"{self.TDARR_USEABLE_URL}/get-nodes"

        self.STATUS = f"{self.TDARR_USEABLE_URL}/status"

        self.MOD_WORKER_LIMIT = f"{self.TDARR_USEABLE_URL}/alter-worker-limit"

        self.SEARCH = f"{self.TDARR_USEABLE_URL}/search-db"

        self.UPDATE_URL = f"{self.TDARR_USEABLE_URL}/cruddb"
