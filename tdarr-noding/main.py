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
    # import lightrun
    try:
        import lightrun

        lightrun.enable(company_key="3fae1797-5c14-498b-80fb-774720b4a8e5")
    except ImportError as e:
        print("Error importing Lightrun: ", e)

    # establish classes
    current_directory = os.getcwd()

    # # debug line
    # current_directory = f"{current_directory}/tdarr-noding"

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
            elif "Refreshed" in Workhorse.Status.state:
                Workhorse.post_refresh()
            elif "Started" or "Normal" in Workhorse.Status.state:
                Workhorse.normal()
        else:
            Workhorse.update_classes()
            Workhorse.startup()
            Workhorse.Status.change_state("Started")

    Workhorse.Status.print_status_file()


main()
