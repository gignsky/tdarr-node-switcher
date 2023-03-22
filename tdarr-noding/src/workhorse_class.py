from . import tdarr
from . import node_interactions

class Workhorse:
    """
    general workhorse for the entireprogram where the large amount of overall processing is handled

    < Document Guardian | Protect >
    """

    # main methods
    def refresh(self):
        Logic.refresh_all(self.Constants)

    def normal(self):
        if self.script_status_file == "Stopped":
            self.startup()
        else:
            print("PLACEHOLDER")
            # TODO Write info in for reading yaml status file and the rest of what to do after startup has finished executing

    def startup(self,Server,node_dictionary,configuration_class):
        """
        startup function: this will run at the inital start of the script when no status file exists
        < Document Guardian | Protect >
        """
        # initiate start up

        ## get nodes output
        get_nodes_output=tdarr.Tdarr_Logic.generic_get_nodes(Server)

        ## update configuration class with tdarr info
        configuration_class.startup_update_nodes_with_tdarr_info(node_dictionary,get_nodes_output)

        # find quantity of online nodes
        quantity_of_living_nodes = 0
        current_priority_level = 0
        for node in node_dictionary:
            node_class = node_dictionary[node]
            line_state = node_class.online
            priority_level = node_class.priority
            if line_state:
                quantity_of_living_nodes += 1
                if priority_level >= current_priority_level:
                    current_priority_level = priority_level

            #reset node to zero workers
            tdarr.Tdarr_Logic.reset_workers_to_zero(Server,node,node_dictionary)

            #reset node to max worker levels
            tdarr.Tdarr_Logic.reset_workers_to_max_limits(Server,node,node_dictionary)

        if quantity_of_living_nodes > Server.max_nodes:
            print(
                "WARNING: Too many nodes alive; killing last node on the priority list"
            )
            node_interactions.HostLogic.kill_smallest_priority_node(configuration_class,node_dictionary)
            # TODO write script to shutdown single worst priority node

        primary_node = Server.primary_node
        primary_node_class = node_dictionary[primary_node]

        if primary_node_class.online:
            print(f"Primary NODE: `{primary_node}` is ONLINE")
            # TODO CHECK FOR ACTIVE WORK ON OTHER ONLINE NODES THEN PAUSE UNTIL EMPTY BEFORE SHUTTING DOWN AFTER RECHECK
            nodes_with_work_list = tdarr.Tdarr_Logic.find_nodes_with_work(
                self.Constants
            )

            number_of_working_nodes = len(nodes_with_work_list)

            if number_of_working_nodes == 1:
                print("PLACEHOLDER")
                if quantity_of_living_nodes > 1:
                    print("INFO: Shutting/Pausing down all nodes except primary")
                    # TODO shutdown all online nodes except primary
                else:
                    self.refresh()
            else:
                # TODO Same function as above on line 59 looping
                print("PLACEHOLDER")
