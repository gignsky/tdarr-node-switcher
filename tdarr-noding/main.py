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
    status_exists=Workhorse.setup_classes(current_directory)

    # check if server is online
    server_status=src.Logic.server_status_check(Workhorse.Server)

    if server_status=="stop":
        status_class.set_server_status("Offline")
    else:
        status_class.set_server_status("Online")

        #continue establishing classes
        expected_node_class_dictionary=Workhorse.Configuration.setup_configuration_node_dictionary()


        if status_exists:
            pass
        else:
            Workhorse.startup(server_class,expected_node_class_dictionary,configuration_class)
            status_class.change_state("Started")

    status_class.print_server_status()


main()
