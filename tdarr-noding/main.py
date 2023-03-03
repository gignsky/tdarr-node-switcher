"""
    main module responsible for sorting where the program should pick up operations
< Document Guardian | Protect >
"""
import sys
import yaml
import src

def main():
    #establish classes
    workhorse_class=src.Workhorse()
    configuration_class=src.Configuration()
    server_class=configuration_class.setup_server_class()
    expected_node_class_dictionary=configuration_class.setup_configuration_node_dictionary()

    #check if configuration file exists
    status_exists=configuration_class.check_if_status_exists()

    if status_exists:
        print("PLACEHOLDER")
    else:
        workhorse_class.startup()
