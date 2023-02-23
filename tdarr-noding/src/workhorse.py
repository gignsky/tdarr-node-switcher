from . import configuration_parsing

class Workhorse:
    @staticmethod
    def setup_constants(configuration_file):
        constants = configuration_parsing.Constants_Setup(configuration_file)
        # constants.Server.determine_tdarr_nodes(
        #     tdarr.Tdarr_Logic.generic_get_nodes(constants)
        # )
        constants.get_nodes_check(tdarr.Tdarr_Logic.generic_get_nodes(constants))

def normal(constants):
    script_status_file = src.Logic.script_status(constants)

    if script_status_file == "Stopped":
        startup(constants)
    else:
        print("PLACEHOLDER")
        # TODO Write info in for reading yaml status file


def startup(constants):
    # initate start up
    expected_node_status = src.tdarr.Tdarr_Logic.alive_node_search(constants)
    quantity_of_living_nodes = 0

    for node in expected_node_status:
        print(f"NODE: `{node}` is {expected_node_status[node]}")
        if expected_node_status[node] == "Online":
            quantity_of_living_nodes += 1

    if quantity_of_living_nodes > constants.max_nodes:
        print("WARNING: Too many nodes alive; killing last node on the priority list")
        # TODO write script to shutdown single worst priority node

    primary_node = constants.primary_node_name

    if expected_node_status[primary_node] == "Online":
        print(f"Primary NODE: `{primary_node}` is ONLINE")
        # TODO CHECK FOR ACTIVE WORK ON OTHER ONLINE NODES THEN PAUSE UNTIL EMPTY BEFORE SHUTTING DOWN AFTER RECHECK
        nodes_with_work_list = src.tdarr.Tdarr_Logic.find_nodes_with_work(constants)

        number_of_working_nodes = len(nodes_with_work_list)

        if number_of_working_nodes == 1:
            print("PLACEHOLDER")
            if quantity_of_living_nodes > 1:
                print("INFO: Shutting/Pausing down all nodes except primary")
                # TODO shutdown all online nodes except primary
            else:
                refresh(constants)
        else:
            # TODO Same function as above on line 59 looping
            print("PLACEHOLDER")
