from . import HostCommands
class HostLogic:
    @staticmethod
    def kill_smallest_priority_node(constants,node_dictionary):
        """
        kill_smallest_priority_node kills the node with the highest priority number

        Args:
            node_dictionary (dict): keys are node names values are assoicated classes
        < Document Guardian | Protect >
        """
        high_priority_node_name= HostLogic.get_node_with_highest_priority(node_dictionary)
        shutdown_command=node_dictionary[high_priority_node_name].shutdown
        HostCommands.shutdown_node(constants,shutdown_command)

    @staticmethod
    def get_node_with_highest_priority(node_dictionary):
        max_priority_level=0
        max_priority_online_node_name=""
        for node_name in node_dictionary:
            if node_dictionary[node_name].online:
                current_priority=node_dictionary[node_name].priority
                if current_priority > max_priority_level:
                    max_priority_level=current_priority
                    max_priority_online_node_name=node_name

        return max_priority_online_node_name