import sys
import yaml
import src

with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/configuration.yml", "r"
) as file:
    configuration = yaml.safe_load(file)


def main():
    # establish constants
    constants = src.Constants(configuration)

    try:
        entered_argument = sys.argv[1]
        if entered_argument == "refresh":
            argument_status_indicator = "refresh"
    except IndexError:
        argument_status_indicator = "normal"

    tdarr_server_status = src.Logic.server_status_check(constants)

    if tdarr_server_status != "stop":
        if argument_status_indicator == "refresh":
            src.Logic.refresh_all(constants)
        elif argument_status_indicator == "normal":
            normal(constants)
    else:
        print("Tdarr Server is DOWN :(")


def normal(constants):
    status_of_script = src.Logic.script_status(constants)


main()
