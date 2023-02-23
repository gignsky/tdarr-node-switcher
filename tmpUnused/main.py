import sys
from os.path import exists
from pprint import pprint
from datetime import datetime
import requests
import src

# get argument if added
try:
    ARGUMENT = sys.argv[1]
    ARGUMENT = "refresh"
except IndexError:
    ARGUMENT = "normal"


def main():
    Config = src.Config()
    if ARGUMENT == "refresh":
        print("Refreshing...")
        src.Tdarr_Orders.update_health_checks()
        src.Tdarr_Orders.update_failed_transcodes()
        src.Tdarr_Orders.update_successful_transcodes()
    elif ARGUMENT == "normal":
        # check tdarr-server status
        status_of_tdarr = src.Logic.status(Config.STATUS)
        if status_of_tdarr == "stop":
            print("Server Not Running")
            return

        situation = src.Logic.discoverSituation(Config.GET_NODES)

        # stopped or running initiates a do nothing
        if situation == "stopped":
            print("stopped")
            return
        if situation == "running":
            print("running")
            return

        # fix start tdarr-node if broken
        if situation == "broken":
            src.Logic.mod_darr_node("up")
            print("broken")

        # run if ganoslal just started
        if situation == "starting":
            print("starting...")
            src.Logic.mod_darr_node("down")
            src.Tdarr_Orders.update_health_checks()
            src.Tdarr_Orders.update_failed_transcodes()
            src.Tdarr_Orders.update_successful_transcodes()

        # run if ganoslal has stopped being a node
        elif situation == "stopping":
            print("stopping...")
            src.Tdarr_Orders.del_running()
            src.Tdarr_Orders.mod_darr_node("up")
            src.Tdarr_Orders.update_successful_transcodes()
    else:
        print("ARGV ERROR")


main()
