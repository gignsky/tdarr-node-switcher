import sys
import yaml
import src

with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/configuration.yml", "r"
) as file:
    configuration = yaml.safe_load(file)

constants = src.Constants(configuration)

try:
    entered_argument = sys.argv[1]
    if entered_argument == "refresh":
        ARGUMENT = "refresh"
except IndexError:
    ARGUMENT = "normal"

if ARGUMENT == "refresh":
    src.Logic.refresh_all(constants)
