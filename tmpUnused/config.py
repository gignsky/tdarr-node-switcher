class Config:
    def __init__(self):
        # CONSTANTS
        ##SET THESE
        TDARR_URL = "http://192.168.51.30:8265"

        # DARR_NODE_HEALTH_NODES = 1
        # DARR_NODE_TRANSCODE_NODES = 1

        # GANOSLAL_NODE_HEALTH_NODES_CPU = 0
        # GANOSLAL_NODE_TRANSCODE_NODES_CPU = 0
        #
        # GANOSLAL_NODE_HEALTH_NODES_GPU = 0
        # GANOSLAL_NODE_TRANSCODE_NODES_GPU = 0

        ###########################################

        api_string = "/api/v2"

        self.set_up_selfs(TDARR_URL, api_string)

    def set_up_selfs(self, TDARR_URL, api_string):
        ######################################
        self.TDARR_USEABLE_URL = f"{TDARR_URL}{api_string}"
        ######################################

        self.GET_NODES = f"{self.TDARR_USEABLE_URL}/get-nodes"

        self.STATUS = f"{self.TDARR_USEABLE_URL}/status"

        self.MOD_WORKER_LIMIT = f"{self.TDARR_USEABLE_URL}/alter-worker-limit"

        self.SEARCH = f"{self.TDARR_USEABLE_URL}/search-db"

        self.UPDATE_URL = f"{self.TDARR_USEABLE_URL}/cruddb"
