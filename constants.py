# CONSTANTS

##SET THESE
TDARR_URL = "https://tdarr.gignsky.com"

DARR_NODE_HEALTH_NODES = 1
DARR_NODE_TRANSCODE_NODES = 1

# GANOSLAL_NODE_HEALTH_NODES_CPU = 0
# GANOSLAL_NODE_TRANSCODE_NODES_CPU = 0
#
# GANOSLAL_NODE_HEALTH_NODES_GPU = 0
# GANOSLAL_NODE_TRANSCODE_NODES_GPU = 0

###########################################

API_STRING = "/api/v2"

######################################
TDARR_USEABLE_URL = TDARR_URL + API_STRING
######################################

GET_NODES = TDARR_USEABLE_URL + "/get-nodes"

STATUS = TDARR_USEABLE_URL + "/status"

MOD_WORKER_LIMIT = TDARR_USEABLE_URL + "/alter-worker-limit"

SEARCH = TDARR_USEABLE_URL + "/search-db"

UPDATE_URL = TDARR_USEABLE_URL + "/cruddb"
