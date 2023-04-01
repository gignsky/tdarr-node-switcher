import yaml
from src import Workhorse
from src.tdarr import Tdarr_Logic
from src.configuration_parsing import ConstantsSetup

with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/tests/test_configuration.yml",
    "r",
) as file:
    configuration_file = yaml.safe_load(file)


def test_init():
    assert ConstantsSetup(configuration_file)


def test_setup_server_class():
    Class = ConstantsSetup(configuration_file)
    assert Class.setup_server_class()


def test_setup_node_class():
    WorkhorseClass = Workhorse()
    Server, node_dictionary = WorkhorseClass.setup_constants(configuration_file)
    get_nodes_output = Tdarr_Logic.generic_get_nodes(Server)
    Class = ConstantsSetup(configuration_file)
    assert Class.setup_node_class(get_nodes_output)
