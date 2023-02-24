import yaml
from src import Logic, Workhorse


with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/tests/test_configuration.yml",
    "r",
) as file:
    configuration_file = yaml.safe_load(file)

WorkhorseClass = Workhorse()
Server, node_dictionary = WorkhorseClass.setup_constants(configuration_file)


def test_server_status_check():
    assert Logic.server_status_check(Server) == "stop" or "alive"


def test_script_status():
    assert Logic.script_status(WorkhorseClass.Constants)
