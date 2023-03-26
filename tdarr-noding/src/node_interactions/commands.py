import os
import subprocess


class HostCommands:
    @staticmethod
    def shutdown_node(Configuration, shutdown_command):
        os.chdir(Configuration.Constants.ansible_folder_path)
        if shutdown_command is not None:
            subprocess.call(shutdown_command)
        else:
            print("ERROR: Cannot shutdown node as there is no shutdown command")

    @staticmethod
    def start_node(NodeClass):
        print("PLACEHOLDER")
