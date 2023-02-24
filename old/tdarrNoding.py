# logic for tdarr switching

import sys
from datetime import datetime
import json
import requests
import touch
from pprint import pprint
from os.path import exists
from orders import (
    del_running,
    start_node,
    stop_node,
    darrWorkerMod,
    update_currently_processing,
    update_failed_transcodes,
    update_health_checks,
    update_successful_transcodes,
)
from constants import (
    DARR_NODE_HEALTH_NODES,
    DARR_NODE_TRANSCODE_NODES,
    GET_NODES,
    MOD_WORKER_LIMIT,
    STATUS,
)

# get argument if added
try:
    arg = sys.argv[1]
    arg = "refresh"
except IndexError:
    arg = "normal"


def main():
    if arg == "refresh":
        print("Refreshing...")
        update_health_checks()
        update_failed_transcodes()
        update_successful_transcodes()
    elif arg == "normal":
        # check tdarr-server status
        status_of_tdarr = status()
        if status_of_tdarr == "stop":
            print("Server Not Running")
            return

        situation = discoverSituation()

        # stopped or running initiates a do nothing
        if situation == "stopped":
            print("stopped")
            return
        if situation == "running":
            print("running")
            return

        # fix start tdarr-node if broken
        if situation == "broken":
            mod_darr_node("up")
            print("broken")

        # run if ganoslal just started
        if situation == "starting":
            print("starting...")
            mod_darr_node("down")
            update_health_checks()
            update_failed_transcodes()
            update_successful_transcodes()

        # run if ganoslal has stopped being a node
        elif situation == "stopping":
            print("stopping...")
            del_running()
            mod_darr_node("up")
            update_successful_transcodes()
    else:
        print("ARGV ERROR")


def status():
    var = requests.get(STATUS)

    if var.status_code != 200:
        print("Tdarr NOT alive!")
        return "stop"


def getNodes():
    """gets current nodes on tdarr

    Returns:
        thing: unformatted json
    """

    var = requests.get(GET_NODES)

    return var


def discoverSituation():
    """discovers the current situation for ganoslal node

    Returns:
        situation: string (either "starting" or "stopping")
    """

    var = getNodes()

    # load into json format
    jsonVar = json.loads(var.text)
    # pprint(jsonVar)

    # figures out the situation
    situation = nodeLogic(jsonVar)

    return situation


def nodeLogic(get_nodes_output_in_json):
    # assign input to var
    var = get_nodes_output_in_json

    # find if both are working and online
    darr = darrTest(var)
    ganos = ganoslalTest(var)
    file_check = exists("/root/tdarr-node-switcher/running")

    # testing of output for test modules
    # pprint("darr: " + darr)
    # pprint("GanosLal: " + ganos)

    if file_check == True:
        if ganos == "Online":
            return "running"

        elif ganos == "Offline":
            return "stopping"

        elif darr == "Online":
            mod_darr_node("down")
            return "broken"

    elif file_check == False:
        if ganos == "Offline":
            return "stopped"

        elif ganos == "Online":
            touch.touch(
                "/home/gig/local_repos/tdarr-node-switcher/tdarr-node-switcher/running"
            )  # TODO Make changeable to current system and have file be placed in current directory
            return "starting"


def darrTest(var):
    try:
        tdarr_node_online_status = var["darr-Node"]
        tdarr_node_online_status = "Online"
    except KeyError:
        tdarr_node_online_status = "Offline"

    return tdarr_node_online_status


def ganoslalTest(var):
    try:
        ganosLal_node_online_status = var["ganosLal"]
        ganosLal_node_online_status = "Online"
    except KeyError:
        ganosLal_node_online_status = "Offline"

    return ganosLal_node_online_status


def mod_darr_node(upOrDown):
    if upOrDown == "up":
        start_node
    # Startup Darr Node
    darrWorkerMod(MOD_WORKER_LIMIT, DARR_NODE_HEALTH_NODES, upOrDown, "healthCPU")
    darrWorkerMod(MOD_WORKER_LIMIT, DARR_NODE_TRANSCODE_NODES, upOrDown, "transcodeCPU")
    if upOrDown == "down":
        update_currently_processing()
        stop_node


main()
PRINTLINE = "=============================="
print(PRINTLINE)
now = datetime.now()
print("Finished at: ")
print(now)
print(PRINTLINE)