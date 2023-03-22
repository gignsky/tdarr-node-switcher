"""
    main module responsible for sorting where the program should pick up operations
    < Document Guardian | Protect >
"""
import os
import src


def main():
    #establish classes
    workhorse_class=src.Workhorse()

    current_directory=os.getcwd()
    configuration_class=src.Configuration(current_directory)

    server_class=configuration_class.setup_server_class()

    #check if configuration file exists
    status_exists,status_file=configuration_class.check_if_status_exists()

    status_class=src.StatusTracking(status_file)

    # check if server is online
    server_status=src.Logic.server_status_check(server_class)

    if server_status=="stop":
        status_class.set_server_status("Offline")
    else:
        status_class.set_server_status("Online")

        #continue establishing classes
        expected_node_class_dictionary=configuration_class.setup_configuration_node_dictionary()


        if status_exists:
            pass
        else:
            workhorse_class.startup(server_class,expected_node_class_dictionary,configuration_class)
            status_class.mark_started(configuration_class)

main()
