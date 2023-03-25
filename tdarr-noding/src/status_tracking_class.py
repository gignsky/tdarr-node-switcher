import yaml

class StatusTracking:
    def __init__(self, status_file,path):
        self.status_dict={"state": "Initalizing"}
        self.path=path
        if status_file is None:
            self.status_file = None
        else:
            self.status_file = status_file
            self.state = status_file["state"]

    #print output
    def print_status_file(self):
        with open(self.path,"w") as file:
            server_status_file_output=yaml.dump(self.status_dict, file)

    #modify stuff
    def set_server_status(self,server_status):
        self.status_dict["tdarr_server"]={"state": server_status}

    def change_state(self, state):
        self.status_dict["state"]=state

    #importing
    def import_server_status(self):
        """
        import_server_status reads yml file to import server status into status class
        """

        status_server_section=self.status_file["tdarr_server"]

        self.ServerStatus=ServerStatus(status_server_section)

        #set up node status dictionary
        self.node_status_dictionary={}

        for name, inner_dictionary in self.ServerStatus.tdarr_nodes_status_dictionary.items():
            self.node_status_dictionary[name]=NodeStatus(name,inner_dictionary)

class ServerStatus:
    def __init__(self, status_server_section):
        self.state=status_server_section["state"]

        #setup basic node info
        tdarr_nodes_section_dictionary=status_server_section["tdarr_nodes"]

        #initalize var
        self.tdarr_nodes_status_dictionary={}

        for name in tdarr_nodes_section_dictionary:
            self.tdarr_nodes_status_dictionary[name]=tdarr_nodes_section_dictionary[name]

class NodeStatus:
    def __init__(self, name, node_status_section):
        self.name=name
        self.node_status_section=node_status_section
        self.state=self.node_status_section["state"]
        self.directive=self.node_status_section["directive"]

    def update_line_state(self,current_line_state):
        if current_line_state:
            self.state="Online"
        else:
            self.state="Offline"
