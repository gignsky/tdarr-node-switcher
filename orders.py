import json

# from pprint import pprint
import subprocess
import requests

from constants import DARR_NODE_TRANSCODE_NODES, MOD_WORKER_LIMIT, SEARCH, UPDATE_URL


def stop_node():
    subprocess.run(["systemctl", "stop", "tdarr-node.service"])


def start_node():
    subprocess.run(["systemctl", "start", "tdarr-node.service"])


# mod workers darr-node
def darrWorkerMod(url, runs, increaseOrDecrease, worker):

    if increaseOrDecrease == "up":
        change = "increase"
    elif increaseOrDecrease == "down":
        change = "decrease"

    if worker == "healthCPU":
        workerType = "healthcheckcpu"
    elif worker == "transcodeCPU":
        workerType = "transcodecpu"

    # actual logic
    i = 0
    while i != runs:
        payload = {
            "data": {
                "nodeID": "darr-Node",
                "process": change,
                "workerType": workerType,
            }
        }
        headers = {"Content-Type": "application/json"}

        requests.post(url, json=payload, headers=headers)

        i = i + 1


def update_health_checks():
    ids = search_for_failed_health_checks()

    i = 0

    for i in ids:
        payload = {
            "data": {
                "collection": "FileJSONDB",
                "mode": "update",
                "docID": i,
                "obj": {"HealthCheck": "Queued"},
            }
        }
        headers = {"Content-Type": "application/json"}

        requests.post(UPDATE_URL, json=payload, headers=headers)

        # pprint(response)


def search_for_failed_health_checks():
    payload = {
        "data": {
            "string": "Error",
            "lessThanGB": 100,
            "greaterThanGB": 0,
        }
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(SEARCH, json=payload, headers=headers)

    response = json.loads(response.text)

    # print(len(response))
    fails = []
    for i in response:
        id = i.get("_id")

        healthCheckStatus = i.get("HealthCheck")
        # print(healthCheckStatus)
        if healthCheckStatus == "Error":
            fails.append(id)
            # print(i)

    return fails


def update_failed_transcodes():
    ids = search_for_failed_transcodes_checks()

    i = 0

    for i in ids:
        payload = {
            "data": {
                "collection": "FileJSONDB",
                "mode": "update",
                "docID": i,
                "obj": {"TranscodeDecisionMaker": "Queued"},
            }
        }
        headers = {"Content-Type": "application/json"}

        requests.post(UPDATE_URL, json=payload, headers=headers)

        # pprint(response)


def search_for_failed_transcodes_checks():
    payload = {
        "data": {
            "string": "Transcode error",
            "lessThanGB": 100,
            "greaterThanGB": 0,
        }
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(SEARCH, json=payload, headers=headers)

    response = json.loads(response.text)

    # print(len(response))
    transcodeErrors = []
    for i in response:
        id = i.get("_id")

        transcodeErrors.append(id)
        # print(i)

    return transcodeErrors


def update_successful_transcodes():
    ids = search_for_successful_transcodes_checks()

    i = 0

    for i in ids:
        payload = {
            "data": {
                "collection": "FileJSONDB",
                "mode": "update",
                "docID": i,
                "obj": {"TranscodeDecisionMaker": "Queued"},
            }
        }
        headers = {"Content-Type": "application/json"}

        requests.post(UPDATE_URL, json=payload, headers=headers)

        # pprint(response)


def search_for_successful_transcodes_checks():
    payload = {
        "data": {
            "string": "Transcode success",
            "lessThanGB": 100,
            "greaterThanGB": 0,
        }
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(SEARCH, json=payload, headers=headers)

    response = json.loads(response.text)

    # print(len(response))
    transcodeSuccesses = []
    for i in response:
        id = i.get("_id")

        transcodeSuccesses.append(id)
        # print(i)

    return transcodeSuccesses


# def requeue_failed_health_checks():
#
# def requeue_failed_transcodes():
update_successful_transcodes()
