"""
    main module responsible for sorting where the program should pick up operations
    < Document Guardian | Protect >
"""
import os
import src


def main():
    #establish classes
    Workhorse=src.Workhorse()

    current_directory=os.getcwd()

    Workhorse.setup_classes(current_directory)

    # check if server is online
    server_status=src.Logic.server_status_check(Workhorse.Server)

    if server_status=="stop":
        Workhorse.Status.set_server_status("Offline")
    else:
        Workhorse.Status.set_server_status("Online")

        if Workhorse.status_exists:
            pass
        else:
            Workhorse.startup(expected_node_class_dictionary)
            Workhorse.Status.change_state("Started")

    Workhorse.Status.print_server_status()


main()
