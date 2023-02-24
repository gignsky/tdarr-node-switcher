import yaml
from src.configuration_parsing import Node

with open(
    "/home/gig/local_repos/tdarr-node-switcher/tdarr-noding/tests/test_configuration.yml",
    "r",
) as file:
    configuration_file = yaml.safe_load(file)


def test_init():
    nodes_dictionary = configuration_file["tdarr_nodes"]
    for node_name in nodes_dictionary:
        inner_dictionary = nodes_dictionary[node_name]
        NodeClass = Node(node_name, inner_dictionary, "Expected")

        assert NodeClass.node_name == node_name
        assert NodeClass.config_node_inner_dictionary == inner_dictionary
        assert NodeClass.priority == inner_dictionary["priority"]
        assert NodeClass.primary_node == True or False
        assert NodeClass.online == None


# def test_set_healthcheck_limits():
#     nodes_dictionary = configuration_file["tdarr_nodes"]
#     list_of_node_classes=[]
#     for node_name in nodes_dictionary:
#         inner_dictionary = nodes_dictionary[node_name]
#         NodeClass = Node(node_name, inner_dictionary, "Expected")
#         list_of_node_classes.append(NodeClass)

# def test_set_transcode_limits():
#     nodes_dictionary = configuration_file["tdarr_nodes"]
#     list_of_node_classes=[]
#     for node_name in nodes_dictionary:
#         inner_dictionary = nodes_dictionary[node_name]
#         NodeClass = Node(node_name, inner_dictionary, "Expected")
#         list_of_node_classes.append(NodeClass)


def test_update_with_tdarr_dictionary():
    nodes_dictionary = configuration_file["tdarr_nodes"]
    list_of_node_classes = []
    for node_name in nodes_dictionary:
        inner_dictionary = nodes_dictionary[node_name]
        NodeClass = Node(node_name, inner_dictionary, "Expected")
        list_of_node_classes.append(NodeClass)

    fake_get_nodes_output = {"_id": "p3x252"}
    for Class in list_of_node_classes:
        Class.update_with_tdarr_dictionary(fake_get_nodes_output, "Expected")
        assert Class.expected == True
        Class.update_with_tdarr_dictionary(fake_get_nodes_output, "Unexpected")
        assert Class.expected == False
        assert Class.tdarr_node_inner_dictionary == fake_get_nodes_output
        assert Class.id_string == "p3x252"


def test_expected_or_not():
    nodes_dictionary = configuration_file["tdarr_nodes"]
    list_of_node_classes = []
    for node_name in nodes_dictionary:
        inner_dictionary = nodes_dictionary[node_name]
        NodeClass = Node(node_name, inner_dictionary, "Expected")
        list_of_node_classes.append(NodeClass)

    for Class in list_of_node_classes:
        Class.expected_or_not("Expected")
        assert Class.expected == True
        Class.expected_or_not("Unexpected")
        assert Class.expected == False
