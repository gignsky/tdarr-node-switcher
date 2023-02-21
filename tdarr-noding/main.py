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
    script_status_file = src.Logic.script_status(constants)

    if script_status_file == "Stopped":
        # initate start up
        expected_node_status = src.tdarr.Tdarr_Logic.alive_node_search(constants)
        quantity_of_living_nodes = 0

        for node in expected_node_status:
            print(f"NODE: `{node}` is {expected_node_status[node]}")
            if expected_node_status[node]=="Online":
                quantity_of_living_nodes += 1

        if quantity_of_living_nodes > constants.max_nodes:
            print("WARNING: Too many nodes alive; killing last node on the priority list")
            #TODO write script to shutdown single worst priority node

        primary_node = constants.primary_node_name

        if expected_node_status[primary_node] == "Online":
            print(f"Primary NODE: `{primary_node}` is ONLINE")
            # TODO CHECK FOR ACTIVE WORK ON OTHER ONLINE NODES THEN PAUSE UNTIL EMPTY BEFORE SHUTTING DOWN AFTER RECHECK


main()
