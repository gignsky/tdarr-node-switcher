import yaml
from src import Workhorse
from src.tdarr import Tdarr_Logic

with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/tests/test_configuration.yml",
    "r",
) as file:
    configuration_file = yaml.safe_load(file)

WorkhorseClass = Workhorse()
Server, node_dictionary = WorkhorseClass.setup_constants(configuration_file)


def test_generic_get_nodes():
    assert Tdarr_Logic.generic_get_nodes(Server)


def test_find_nodes_with_work():
    assert Tdarr_Logic.find_nodes_with_work(Server)


def test_search_for_failed_health_checks():
    assert Tdarr_Logic.search_for_failed_health_checks(Server)


def test_payload_and_headers():
    proper_payload = {
        "data": {
            "string": "test",
            "lessThanGB": 100,
            "greaterThanGB": 0,
        }
    }
    return_payload, return_header = Tdarr_Logic.payload_and_headers("test")

    assert proper_payload == return_payload
