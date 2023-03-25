import time
from . import Configuration as ConfigurationClass
from . import StatusTracking
from . import tdarr
from . import node_interactions
from . import Logic

class Workhorse:
    """
    general workhorse for the entireprogram where the large amount of overall processing is handled

    < Document Guardian | Protect >
    """

    # main methods
    def setup_classes(self,current_directory):
        """
        setup_classes setup classes to be used each time the program runs

        Args:
            current_directory (str): path to current working directory of main.py

        < Document Guardian | Protect >
        """
        self.root_dir=current_directory
        self.Configuration=ConfigurationClass(self.root_dir)

        self.Server=self.Configuration.setup_server_class()

        #check if configuration file exists
        self.status_exists,self.status_file=self.Configuration.check_if_status_exists()

        self.Status=StatusTracking(self.status_file,self.Configuration.STATUS_PATH)

        self.node_dictionary=self.Configuration.setup_configuration_node_dictionary()

    def update_nodes_output(self):
        """
        update_nodes_output updates self.get_nodes_output to most current pull from tdarr server
        < Document Guardian | Protect >
        """
        self.get_nodes_output=tdarr.Tdarr_Logic.generic_get_nodes(self.Server)

    def update_classes(self):
        """
        update_classes update classes with current information
        < Document Guardian | Protect >
        """
        # refresh get_nodes_output
        self.update_nodes_output()

        #refresh tdarr node classes
        list_of_alive_tdarr_nodes=[]

        for node_id in self.get_nodes_output:
            inner_tdarr_dictionary=self.get_nodes_output[node_id]
            node_name=inner_tdarr_dictionary["nodeName"]
            list_of_alive_tdarr_nodes.append(node_name)

        for name, Class in self.node_dictionary.items():

            #run update in node class
            if name in list_of_alive_tdarr_nodes:
                for node_id in self.get_nodes_output:
                    inner_tdarr_dictionary=self.get_nodes_output[node_id]
                    Class.update_node("Online",inner_tdarr_dictionary)
            else:
                Class.update_node("Offline")

        #refresh status class
        self.Status.status_update()

    def startup(self):
        """
        startup function: this will run at the inital start of the script when no status file exists

            The purpose of this function is to reset the nodes and server to a known point in order to begin noding.

            steps to be taken in this function:
            1. get inital tdarr get_nodes output and update the classes with relevant information
            2. ensure that more than the max nodes number is not running at once, and if found to be true shutdown nodes with smallest priority
            3. ensure that all nodes are set to zero workers
            4. kill nodes without active work
            5. run workhorse update function to update config with most current information
        < Document Guardian | Protect >
        """
        # initiate start up

        ## 1
        ### 1.a get_nodes output
        self.update_nodes_output()

        ### 1.b update configuration class with tdarr info
        self.Configuration.startup_update_nodes_with_tdarr_info(self.node_dictionary,self.get_nodes_output)

        ## 2
        quantity_of_living_nodes=999 # set quantity of living nodes to an absurdly high number to allow for looping on next section

        ### 2.a - begin looping to kill lowest priority nodes
        while quantity_of_living_nodes > self.Server.max_nodes:
            quantity_of_living_nodes = Logic.find_quant_living_nodes(self.node_dictionary)

            if quantity_of_living_nodes > self.Server.max_nodes:
                print(
                    "WARNING: Too many nodes alive; killing last node on the priority list"
                )
                highest_priority_node_name=node_interactions.HostLogic.kill_smallest_priority_node(self.Configuration,self.node_dictionary)

                # set node state to offline
                self.node_dictionary[highest_priority_node_name].line_state("Offline")

        # commented out for new system of work
        # Logic.reset_node_workers(self.Server,self.node_dictionary)

        ## 3
        for node_name, node_class in self.node_dictionary.items():
            if node_class.online:
                tdarr.Tdarr_Orders.reset_workers_to_zero(self.Server,node_name,self.node_dictionary)


        ## 4
        _, nodes_without_work_list = tdarr.Tdarr_Logic.find_nodes_with_work(self.Server)

        #shutdown nodes without work
        for node in nodes_without_work_list:
            for node_dict_name in self.node_dictionary:
                if node == node_dict_name:
                    #set workers to zero
                    tdarr.Tdarr_Orders.reset_workers_to_zero(self.Server,node,self.node_dictionary)
                    #order shutdown
                    node_interactions.HostLogic.kill_node(self.Configuration,self.node_dictionary,node)
                    #set node status to offline
                    self.node_dictionary[node_dict_name].line_state("Offline")

        # primary_node = self.Server.primary_node
        # primary_node_class = self.node_dictionary[primary_node]

#         if primary_node_class.online:
#             print(f"Primary NODE: `{primary_node}` is ONLINE")
#             # TODO CHECK FOR ACTIVE WORK ON OTHER ONLINE NODES THEN PAUSE UNTIL EMPTY BEFORE SHUTTING DOWN AFTER RECHECK
#
#             number_of_working_nodes = len(nodes_with_work_list)
#
#             if number_of_working_nodes == 1:
#                 print("PLACEHOLDER")
#                 if quantity_of_living_nodes > 1:
#                     print("INFO: Shutting/Pausing down all nodes except primary")
#                     # TODO shutdown all online nodes except primary
#                 else:
#                     self.refresh()
#             else:
#                 # TODO Same function as above on line 59 looping
#                 print("PLACEHOLDER")

    def refresh(self):
        Logic.refresh_all(self.Server)

    # def normal(self):
    #     if self.script_status_file == "Stopped":
    #         self.startup()
    #     else:
    #         print("PLACEHOLDER")
    #         # TODO Write info in for reading yaml status file and the rest of what to do after startup has finished executing
