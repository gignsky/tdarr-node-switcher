import os
import subprocess


class HostCommands:
    @staticmethod
    def shutdown_node(Configuration, shutdown_command):
        """
        shutdown_node shuts a node down

        Args:
            Configuration (Class): the configuration class
            shutdown_command (list): list of the non-space characters in the string command that would shutdown a node
        < Document Guardian | Protect >
        """
        os.chdir(Configuration.Constants.ansible_folder_path)
        if shutdown_command is not None:
            subprocess.call(shutdown_command)
        else:
            print("ERROR: Cannot shutdown node as there is no shutdown command")

    @staticmethod
    def startup_node(Configuration, startup_command):
        """
        startup_node starts a node

        Args:
            Configuration (Class): the configuration class
            startup_command (list): list of the non-space characters in the string command that would shutdown a node
        < Document Guardian | Protect >
        """
        os.chdir(Configuration.Constants.ansible_folder_path)
        if startup_command is not None:
            subprocess.call(startup_command)
            return False
        else:
            print("ERROR: Cannot start node as there is no startup command")
            return True
