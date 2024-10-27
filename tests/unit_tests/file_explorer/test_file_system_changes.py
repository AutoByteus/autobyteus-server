import pytest
from autobyteus_server.file_explorer.file_system_changes import (
    ChangeType,
    FileSystemChange,
    AddChange,
    DeleteChange,
    RenameChange,
    FileSystemChangeEvent,
    serialize_change_event,
    deserialize_change_event
)
from autobyteus_server.file_explorer.tree_node import TreeNode


def test_change_type_enum():
    assert ChangeType.ADD.value == "add"
    assert ChangeType.DELETE.value == "delete"
    assert ChangeType.RENAME.value == "rename"
    with pytest.raises(ValueError):
        ChangeType("invalid")


def test_file_system_change_serialization():
    change = FileSystemChange(type=ChangeType.ADD)
    change_dict = change.to_dict()
    assert change_dict["type"] == "add"
    with pytest.raises(ValueError):
        FileSystemChange.from_dict({"type": "invalid"})


def test_add_change_serialization():
    node = TreeNode(name="file.txt", is_file=True)
    node.id = "123"  # Manually set the id to match the test case
    add_change = AddChange(node=node, parent_id="parent_456")
    add_dict = add_change.to_dict()
    assert add_dict["type"] == "add"
    assert add_dict["node"]["name"] == "file.txt"
    assert add_dict["node"]["path"] == "file.txt"  # Adjusted path based on TreeNode implementation
    assert add_dict["node"]["is_file"] is True
    assert add_dict["node"]["id"] == "123"
    assert add_dict["parent_id"] == "parent_456"

    deserialized = AddChange.from_dict(add_dict)
    assert deserialized.type == ChangeType.ADD
    assert deserialized.node.name == "file.txt"
    assert deserialized.node.get_path() == "file.txt"
    assert deserialized.node.is_file is True
    assert deserialized.node.id == "123"
    assert deserialized.parent_id == "parent_456"


def test_delete_change_serialization():
    delete_change = DeleteChange(node_id="123", parent_id="parent_456")
    delete_dict = delete_change.to_dict()
    assert delete_dict["type"] == "delete"
    assert delete_dict["node_id"] == "123"
    assert delete_dict["parent_id"] == "parent_456"

    deserialized = DeleteChange.from_dict(delete_dict)
    assert deserialized.type == ChangeType.DELETE
    assert deserialized.node_id == "123"
    assert deserialized.parent_id == "parent_456"


def test_rename_change_serialization():
    node = TreeNode(name="new_name.txt", is_file=True)
    node.id = "789"  # Manually set the id to match the test case
    rename_change = RenameChange(node=node, parent_id="parent_456", previous_id="123")
    rename_dict = rename_change.to_dict()
    assert rename_dict["type"] == "rename"
    assert rename_dict["node"]["name"] == "new_name.txt"
    assert rename_dict["node"]["path"] == "new_name.txt"  # Adjusted path based on TreeNode implementation
    assert rename_dict["node"]["is_file"] is True
    assert rename_dict["node"]["id"] == "789"
    assert rename_dict["parent_id"] == "parent_456"
    assert rename_dict["previous_id"] == "123"

    deserialized = RenameChange.from_dict(rename_dict)
    assert deserialized.type == ChangeType.RENAME
    assert deserialized.node.name == "new_name.txt"
    assert deserialized.node.get_path() == "new_name.txt"
    assert deserialized.node.is_file is True
    assert deserialized.node.id == "789"
    assert deserialized.parent_id == "parent_456"
    assert deserialized.previous_id == "123"


def test_file_system_change_event_serialization():
    add_change = AddChange(
        node=TreeNode(name="file1.txt", is_file=True),
        parent_id="parent_1"
    )
    add_change.node.id = "1"
    delete_change = DeleteChange(node_id="2", parent_id="parent_2")
    rename_change = RenameChange(
        node=TreeNode(name="file3_renamed.txt", is_file=True),
        parent_id="parent_3",
        previous_id="3_old"
    )
    rename_change.node.id = "3"
    event = FileSystemChangeEvent(changes=[add_change, delete_change, rename_change])
    event_dict = event.to_dict()

    assert len(event_dict["changes"]) == 3
    assert event_dict["changes"][0]["type"] == "add"
    assert event_dict["changes"][0]["node"]["name"] == "file1.txt"
    assert event_dict["changes"][0]["node"]["path"] == "file1.txt"
    assert event_dict["changes"][0]["node"]["is_file"] is True
    assert event_dict["changes"][0]["node"]["id"] == "1"
    assert event_dict["changes"][0]["parent_id"] == "parent_1"

    assert event_dict["changes"][1]["type"] == "delete"
    assert event_dict["changes"][1]["node_id"] == "2"
    assert event_dict["changes"][1]["parent_id"] == "parent_2"

    assert event_dict["changes"][2]["type"] == "rename"
    assert event_dict["changes"][2]["node"]["name"] == "file3_renamed.txt"
    assert event_dict["changes"][2]["node"]["path"] == "file3_renamed.txt"
    assert event_dict["changes"][2]["node"]["is_file"] is True
    assert event_dict["changes"][2]["node"]["id"] == "3"
    assert event_dict["changes"][2]["parent_id"] == "parent_3"
    assert event_dict["changes"][2]["previous_id"] == "3_old"

    deserialized = FileSystemChangeEvent.from_dict(event_dict)
    assert len(deserialized.changes) == 3
    assert isinstance(deserialized.changes[0], AddChange)
    assert isinstance(deserialized.changes[1], DeleteChange)
    assert isinstance(deserialized.changes[2], RenameChange)


def test_serialize_deserialize_change_event():
    add_change = AddChange(
        node=TreeNode(name="file4.txt", is_file=True),
        parent_id="parent_4"
    )
    add_change.node.id = "4"
    event = FileSystemChangeEvent(changes=[add_change])
    json_data = serialize_change_event(event)
    assert isinstance(json_data, str)

    deserialized_event = deserialize_change_event(json_data)
    assert len(deserialized_event.changes) == 1
    assert isinstance(deserialized_event.changes[0], AddChange)
    assert deserialized_event.changes[0].node.name == "file4.txt"
    assert deserialized_event.changes[0].node.get_path() == "file4.txt"
    assert deserialized_event.changes[0].parent_id == "parent_4"
    assert deserialized_event.changes[0].node.id == "4"


def test_tree_node_serialization():
    node = TreeNode(name="dir", is_file=False)
    node.id = "dir_1"
    child = TreeNode(name="subdir", is_file=False, parent=node)
    child.id = "subdir_1"
    node.add_child(child)
    node_dict = node.to_dict()
    assert node_dict["name"] == "dir"
    assert node_dict["path"] == "dir"
    assert node_dict["is_file"] is False
    assert node_dict["id"] == "dir_1"
    assert len(node_dict["children"]) == 1
    assert node_dict["children"][0]["name"] == "subdir"
    assert node_dict["children"][0]["path"] == "dir/subdir"
    assert node_dict["children"][0]["is_file"] is False
    assert node_dict["children"][0]["id"] == "subdir_1"
    assert node_dict["children"][0]["children"] == []

    deserialized_node = TreeNode.from_dict(node_dict)
    assert deserialized_node.name == "dir"
    assert deserialized_node.get_path() == "dir"
    assert deserialized_node.is_file is False
    assert deserialized_node.id == "dir_1"
    assert len(deserialized_node.children) == 1
    child_node = deserialized_node.children[0]
    assert child_node.name == "subdir"
    assert child_node.get_path() == "dir/subdir"
    assert child_node.is_file is False
    assert child_node.id == "subdir_1"
    assert child_node.children == []