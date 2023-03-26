import yaml

class StatusTracking:
    def __init__(self, status_file,path):
        self.status_dict={"state": "Initalizing"}
        self.path=path
        if status_file is None:
            self.status_file = None
            self.configure_server_status()
        else:
            self.status_file = status_file
            self.state = status_file["state"]
            self.import_server_status()
            self.import_node_status()

    #print output
    def print_status_file(self):
        with open(self.path,"w") as file:
            # server_status_file_output=
            yaml.dump(self.status_dict, file)

    #modify stuff

    def change_state(self, state):
        self.status_dict["state"]=state

    #importing
    def import_server_status(self):
        """
        import_server_status reads yml file to import server status into status class
        """

        status_server_section=self.status_file["tdarr_server"]

        self.ServerStatus=ServerStatus(status_server_section)

    def import_node_status(self):
        #set up node status dictionary
        if len(self.ServerStatus.tdarr_nodes_status_dictionary) != 0:
            self.NodeStatusMaster=NodeStatusMaster(self.ServerStatus.tdarr_nodes_status_dictionary)
        else:
            self.NodeStatusMaster=None

    def configure_server_status(self):
        """
        configure_server_status configures server status class when there is no status file as of yet
        """
        self.ServerStatus=ServerStatus()
        self.import_node_status()

    def startup_configure_node_master(self,node_dictionary):
        self.NodeStatusMaster=NodeStatusMaster(node_dictionary)

    #updates
    def status_update(self):
        #update status dict
        self.ServerStatus.update_server_dict(self.NodeStatusMaster.node_status_dictionary)
        self.status_dict["tdarr_server"]=self.ServerStatus.status_dict

        self.print_status_file()

class ServerStatus:
    def __init__(self, status_server_section=None):
        if status_server_section is not None:
            self.state=status_server_section["state"]
            self.status_dict["state"]=self.state

            #setup basic node info
            tdarr_nodes_section_dictionary=status_server_section["tdarr_nodes"]

            #initalize var
            self.tdarr_nodes_status_dictionary={}

            for name in tdarr_nodes_section_dictionary:
                self.tdarr_nodes_status_dictionary[name]=tdarr_nodes_section_dictionary[name]
        else:
            self.state=None
            self.status_dict={}
            self.tdarr_nodes_status_dictionary={}

    #modify stuff
    def change_state(self, state):
        self.state=state
        self.status_dict["state"]=self.state

    def set_server_status(self,server_status):
        self.status_dict={"state": server_status}

    #add tdarr_nodes_dictionary
    def add_tdarr_nodes(self,tdarr_nodes_dictionary):
        self.tdarr_nodes_section={}

        for name, Class in tdarr_nodes_dictionary.items():
            self.tdarr_nodes_section[name]={"state": Class.state, "directive": Class.directive}

        self.status_dict["tdarr_nodes"]=self.tdarr_nodes_section

    #update stuff
    def update_server_dict(self,node_status_dictionary):
        for name, Class in node_status_dictionary.items():
            Class.update_status_dict()
            self.status_dict[name]=Class.node_status_dict

class NodeStatusMaster:
    def __init__(self, tdarr_nodes_status_dictionary):
        self.node_status_dictionary={}

        for name, inner_dictionary in tdarr_nodes_status_dictionary.items():
            self.node_status_dictionary[name]=NodeStatus(name,inner_dictionary)

    def update_node_master(self):
        #TODO possible placeholder might not need this class
        print("PLACEHOLDER")

class NodeStatus:
    def __init__(self, name, node_status_section):
        self.name=name
        if type(node_status_section)==dict:
            self.node_status_section=node_status_section
            self.state=self.node_status_section["state"]
            self.directive=self.node_status_section["directive"]
        else:
            self.NodeClass=node_status_section
            self.node_status_section=None
            self.update_line_state(self.NodeClass.line_state)
            self.directive="Initalizing"

    def update_line_state(self,current_line_state):
        if current_line_state:
            self.state="Online"
        else:
            self.state="Offline"

    def update_directive(self,new_directive):
        self.directive=new_directive

    def update_status_dict(self):
        self.node_status_dict={"state": self.state, "directive": self.directive}
