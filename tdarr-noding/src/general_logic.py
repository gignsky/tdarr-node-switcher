import time
import requests
import yaml
from . import tdarr
# from . import status_tracking


class Logic:
    @staticmethod
    def refresh_all(constants):
        print("Refreshing...")
        tdarr.Tdarr_Orders.refresh_health_checks(constants)
        tdarr.Tdarr_Orders.update_transcodes(constants)

    @staticmethod
    def server_status_check(Server):
        var = requests.get(Server.status)

        if var.status_code != 200:
            return "stop"
        else:
            print("INFO: Server is ALIVE!")
            return "alive"

    @staticmethod
    def script_status(path):
        try:
            if path.is_file():
                with open(path, "r") as file:
                    status_file = yaml.safe_load(file)
                    return status_file
            else:
                return "Empty"
        except AttributeError:
            return "Empty"

    @staticmethod
    def reset_node_workers(Server,node_dictionary,node_name=None):
        if node_name is None:
            for node in node_dictionary:
                node_class = node_dictionary[node]
                line_state = node_class.online
                if line_state:
                    #reset node to zero workers
                    tdarr.Tdarr_Orders.reset_workers_to_zero(Server,node,node_dictionary)

                    #wait for workers to set to zero
                    time.sleep(2.5)

                    #reset node to max worker levels
                    tdarr.Tdarr_Orders.reset_workers_to_max_limits(Server,node,node_dictionary)
        else:
            for node in node_dictionary:
                node_class = node_dictionary[node]
                if node_name==node:
                    line_state = node_class.online
                    if line_state:
                        #reset node to zero workers
                        tdarr.Tdarr_Orders.reset_workers_to_zero(Server,node,node_dictionary)

                        #wait for workers to set to zero
                        time.sleep(2.5)

                        #reset node to max worker levels
                        tdarr.Tdarr_Orders.reset_workers_to_max_limits(Server,node,node_dictionary)
