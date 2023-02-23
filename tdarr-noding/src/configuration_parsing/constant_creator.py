from . import Server, Node

class Constants_Setup:
    def __init__(self, configuration_file):
        self.program_folder_path = configuration_file["program"]["folder_path"]

        self.setup_server_class(configuration_file)

        self.setup_list_of_node_names(configuration_file)

    def setup_server_class(self,configuration_file):
        server_inner_dict=configuration_file["tdarr_server"]
        self.Server=Server(server_inner_dict)

    def setup_node_class(self.Server.determine_expected_nodes):
        node_inner_dict=
        self.set_primary_node(configuration_file)

