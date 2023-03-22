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

    # check if server is online
    server_status=src.Logic.server_status_check(server_class)
    if server_status=="stop":
        pass
    else:
        #continue establishing classes
        expected_node_class_dictionary=configuration_class.setup_configuration_node_dictionary()

        #check if configuration file exists
        status_exists=configuration_class.check_if_status_exists()

        if status_exists:
            print("PLACEHOLDER") #TODO Configure here for in status non-startup status
        else:
            #TODO configure status file to show that program has begun starting up procedure
            workhorse_class.startup(server_class,expected_node_class_dictionary,configuration_class)

main()
