"""
    main module responsible for sorting where the program should pick up operations
    < Document Guardian | Protect >
"""
import os
import src


def main():
    """
    main core logic for overall project
    < Document Guardian | Protect >
    """
    # establish classes

    current_directory = os.getcwd()

    Workhorse = src.Workhorse(current_directory)

    # check if server is online
    server_status = src.Logic.server_status_check(Workhorse.Server)

    if server_status == "stop":
        Workhorse.Status.ServerStatus.set_server_status("Offline")
    else:
        Workhorse.Status.ServerStatus.set_server_status("Online")

        if Workhorse.status_exists:
            status_state = Workhorse.Status.state
            if "Started" or "Normal" in status_state:
                Workhorse.normal(status_state)
        else:
            Workhorse.update_classes()
            Workhorse.startup()
            Workhorse.Status.change_state("Started")

    Workhorse.Status.print_status_file()


main()
