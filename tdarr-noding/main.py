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
    # ? REMOVED FOR POSSIBLE LATER REIMPLEMENTATION
    #     # import lightrun
    #     try:
    #         import lightrun
    #
    #         lightrun.enable(company_key="3fae1797-5c14-498b-80fb-774720b4a8e5")
    #     except ImportError as e:
    #         print("Error importing Lightrun: ", e)

    # establish classes
    current_directory = os.getcwd()

    # # debug line
    # current_directory = f"{current_directory}/tdarr-noding"

    # check if status file is empty but exists then remove it if thats the case
    def check_and_delete_empty_file(current_directory):
        file_path = os.path.join(current_directory, "status.yml")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                contents = file.read()
            if not contents:
                os.remove(file_path)

    check_and_delete_empty_file(current_directory)

    Workhorse = src.Workhorse(current_directory)

    # check if server is online
    server_status = src.Logic.server_status_check(Workhorse.Server)

    if server_status == "stop":
        Workhorse.Status.ServerStatus.set_server_status("Offline")
    else:
        Workhorse.Status.ServerStatus.set_server_status("Online")

        if Workhorse.status_exists:
            if "Normal_Finished" in Workhorse.Status.state:
                Workhorse.verify_primary_running()
            #!TODO Uncomment these lines when the refresh function is implemented
            # elif "Refreshed" in Workhorse.Status.state:
            #     Workhorse.post_refresh()
            elif "Started" or "Normal" in Workhorse.Status.state:
                Workhorse.normal()
        else:
            Workhorse.update_classes()
            Workhorse.startup()
            Workhorse.Status.change_state("Started")

    Workhorse.update_classes()
    Workhorse.Status.print_status_file()


main()
