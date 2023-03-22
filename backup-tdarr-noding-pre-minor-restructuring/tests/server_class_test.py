import yaml
from src.configuration_parsing import Server

with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/tests/test_configuration.yml",
    "r",
) as file:
    configuration_file = yaml.safe_load(file)

server_inner_dict = configuration_file["tdarr_server"]
node_inner_dict = configuration_file["tdarr_nodes"]


def test_init():
    ServerClass = Server(server_inner_dict)
    assert ServerClass.server_inner_dict == server_inner_dict


def test_expected_nodes_creator():
    ServerClass = Server(server_inner_dict)
    assert ServerClass.expected_nodes_creator(node_inner_dict)


def test_default_server_configuration():
    ServerClass = Server(server_inner_dict)
    assert ServerClass.max_nodes == 4
    assert ServerClass.priority_level == 2


def test_setup_urls():
    ServerClass = Server(server_inner_dict)
    url = server_inner_dict["url"]
    api_key = server_inner_dict["api_string"]
    tdarr_useable_url = f"{url}{api_key}"

    assert ServerClass.get_nodes == f"{tdarr_useable_url}/get-nodes"
    assert ServerClass.status == f"{tdarr_useable_url}/status"
    assert ServerClass.mod_worker_limit == f"{tdarr_useable_url}/alter-worker-limit"
    assert ServerClass.search == f"{tdarr_useable_url}/search-db"
    assert ServerClass.update_url == f"{tdarr_useable_url}/cruddb"
