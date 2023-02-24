import sys
import yaml
import src

with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/configuration.yml", "r"
) as file:
    configuration_file = yaml.safe_load(file)


def main():
    # establish constants
    Workhorse = src.Workhorse()

    Server, node_dictionary = Workhorse.setup_constants(configuration_file)

    # establish if run with refresh command on purpose
    try:
        entered_argument = sys.argv[1]
        if entered_argument == "refresh":
            argument_status_indicator = "refresh"
    except IndexError:
        argument_status_indicator = "normal"

    # check if tdarr server is running
    tdarr_server_status = src.Logic.server_status_check(Server)

    if tdarr_server_status != "stop":
        if argument_status_indicator == "refresh":
            Workhorse.refresh()
        elif argument_status_indicator == "normal":
            Workhorse.normal()
    else:
        print("Tdarr Server is DOWN :(")


main()
