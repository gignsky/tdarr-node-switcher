import os
import subprocess


class HostCommands:
    @staticmethod
    def shutdown_node(Configuration, shutdown_command):
        os.chdir(Configuration.Constants.ansible_folder_path)
        subprocess.call(
            shutdown_command
        )  # TODO START HERE UPON REENTRY you were trying to get this ansible playbook to run as expected when this point is reached

    @staticmethod
    def start_node(NodeClass):
        print("PLACEHOLDER")
