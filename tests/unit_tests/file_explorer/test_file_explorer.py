import json
import os
from pathlib import Path
import tempfile
from typing import Generator

import pytest
from pytest import MonkeyPatch

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.file_explorer.file_system_changes import (
    AddChange,
    DeleteChange,
    FileSystemChangeEvent,
)
from autobyteus_server.file_explorer.tree_node import TreeNode


@pytest.fixture
def temp_workspace() -> Generator[FileExplorer, None, None]:
    """
    Fixture to create a temporary workspace directory using tempfile.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        file_explorer = FileExplorer(workspace_root_path=temp_dir)
        file_explorer.build_workspace_directory_tree()
        yield file_explorer
    # TemporaryDirectory automatically cleans up


def test_build_workspace_directory_tree(temp_workspace: FileExplorer) -> None:
    """
    Test that the workspace directory tree is built correctly.
    """
    assert temp_workspace.root_node is not None
    assert (
        temp_workspace.root_node.name
        == os.path.basename(temp_workspace.workspace_root_path)
    )
    assert not temp_workspace.root_node.is_file


def test_write_file_content_creates_file_and_updates_tree(
    temp_workspace: FileExplorer,
) -> None:
    """
    Test writing file content creates the file and updates the in-memory tree.
    """
    # Define file path and content
    file_path = "test_folder/test_file.txt"
    content = "Hello, World!"

    # Write the file using FileExplorer
    change_event: FileSystemChangeEvent = temp_workspace.write_file_content(
        file_path, content
    )

    # Verify that the file exists on the filesystem
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    assert absolute_file_path.exists()
    assert absolute_file_path.read_text(encoding="utf-8") == content

    # Verify that the in-memory tree has been updated
    parts = file_path.split(os.sep)
    current_node = temp_workspace.root_node
    for part in parts:
        found = False
        for child in current_node.children:
            if child.name == part:
                current_node = child
                found = True
                break
        assert found, f"Node '{part}' not found in the tree."

    assert current_node.is_file

    # Verify the FileSystemChangeEvent
    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 2  # One for directory, one for file
    add_changes = [
        change for change in change_event.changes if isinstance(change, AddChange)
    ]
    assert len(add_changes) == 2
    assert add_changes[1].node.name == "test_file.txt"
    assert add_changes[1].node.is_file


def test_read_file_content_success(temp_workspace: FileExplorer) -> None:
    """
    Test reading file content successfully.
    """
    # Create a file manually
    file_path = "read_test.txt"
    content = "Read this content."
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_file_path.write_text(content, encoding="utf-8")

    # Update the in-memory tree
    temp_workspace.build_workspace_directory_tree()

    # Read the file using FileExplorer
    read_content: str = temp_workspace.read_file_content(file_path)
    assert read_content == content


def test_read_file_content_exceeds_max_size(temp_workspace: FileExplorer) -> None:
    """
    Test that reading a file exceeding max_size raises a ValueError.
    """
    # Create a large file exceeding the max_size
    file_path = "large_file.txt"
    content = "A" * (1024 * 1024 + 1)  # 1MB + 1 byte
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.write_text(content, encoding="utf-8")

    # Update the in-memory tree
    temp_workspace.build_workspace_directory_tree()

    # Attempt to read the file with max_size limit
    with pytest.raises(ValueError) as exc_info:
        temp_workspace.read_file_content(file_path, max_size=1024 * 1024)
    assert "exceeds the maximum allowed size" in str(exc_info.value)


def test_remove_file_or_folder_success(temp_workspace: FileExplorer) -> None:
    """
    Test removing a file or folder successfully.
    """
    # Create a file to remove
    file_path = "remove_test.txt"
    content = "To be removed."
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.write_text(content, encoding="utf-8")

    # Update the in-memory tree
    temp_workspace.build_workspace_directory_tree()

    # Capture the node_id of the file before removal
    parts = file_path.split(os.sep)
    current_node = temp_workspace.root_node
    for part in parts:
        found = False
        for child in current_node.children:
            if child.name == part:
                current_node = child
                found = True
                break
        assert found, f"Node '{part}' not found in the tree."
    file_node_id = current_node.id

    # Remove the file using FileExplorer
    change_event: FileSystemChangeEvent = temp_workspace.remove_file_or_folder(
        file_path
    )

    # Verify that the file has been removed from the filesystem
    assert not absolute_file_path.exists()

    # Verify the FileSystemChangeEvent
    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 1
    delete_change = change_event.changes[0]
    assert isinstance(delete_change, DeleteChange)

    # Assert that the node_id matches the removed file's node_id
    assert delete_change.node_id == file_node_id


def test_remove_nonexistent_file_raises_error(temp_workspace: FileExplorer) -> None:
    """
    Test that removing a nonexistent file raises a ValueError.
    """
    # Attempt to remove a file that does not exist
    with pytest.raises(ValueError) as exc_info:
        temp_workspace.remove_file_or_folder("nonexistent.txt")
    assert "Path not found" in str(exc_info.value)


def test_get_tree_returns_correct_tree(temp_workspace: FileExplorer) -> None:
    """
    Test that get_tree returns the correct in-memory tree.
    """
    # Get the in-memory tree
    tree = temp_workspace.get_tree()
    assert isinstance(tree, TreeNode)
    assert tree.name == os.path.basename(temp_workspace.workspace_root_path)


def test_to_json_returns_valid_json(temp_workspace: FileExplorer) -> None:
    """
    Test that to_json returns a valid JSON representation of the tree.
    """
    # Convert the tree to JSON
    json_repr: str = temp_workspace.to_json()
    assert isinstance(json_repr, str)

    # Load the JSON and verify its structure
    tree_dict = json.loads(json_repr)
    assert "name" in tree_dict
    assert "children" in tree_dict


def test_write_file_outside_workspace_raises_error(temp_workspace: FileExplorer) -> None:
    """
    Test that writing a file outside the workspace raises a ValueError.
    """
    # Attempt to write a file with an absolute path outside the workspace
    with pytest.raises(ValueError) as exc_info:
        temp_workspace.write_file_content("/outside.txt", "Should fail.")
    assert "The path must be relative to the workspace root" in str(exc_info.value)


def test_read_file_outside_workspace_raises_error(temp_workspace: FileExplorer) -> None:
    """
    Test that reading a file outside the workspace raises a ValueError.
    """
    # Attempt to read a file with an absolute path outside the workspace
    with pytest.raises(ValueError) as exc_info:
        temp_workspace.read_file_content("/outside.txt")
    assert "Access denied: File is outside the workspace" in str(exc_info.value)


def test_write_file_without_permission(
    temp_workspace: FileExplorer, monkeypatch: MonkeyPatch
) -> None:
    """
    Test that writing to a file without permission raises a PermissionError.
    """
    # Create a file and simulate write permission denied
    file_path = "protected.txt"
    content = "Cannot write to this file."
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.write_text(content, encoding="utf-8")

    # Mock os.access to simulate no write permission
    original_access = os.access

    def mock_access(path: str, mode: int) -> bool:
        if path == str(absolute_file_path) and mode & os.W_OK:
            return False
        return original_access(path, mode)

    monkeypatch.setattr(os, "access", mock_access)

    # Update the in-memory tree
    temp_workspace.build_workspace_directory_tree()

    # Attempt to write to the protected file
    with pytest.raises(PermissionError) as exc_info:
        temp_workspace.write_file_content(file_path, "New content.")
    assert "Permission denied" in str(exc_info.value)


def test_remove_file_without_permission(
    temp_workspace: FileExplorer, monkeypatch: MonkeyPatch
) -> None:
    """
    Test that removing a file without permission raises a PermissionError.
    """
    # Create a file and simulate write permission denied
    file_path = "protected_remove.txt"
    content = "Cannot remove this file."
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.write_text(content, encoding="utf-8")

    # Mock os.access to simulate no write permission
    original_access = os.access

    def mock_access(path: str, mode: int) -> bool:
        if path == str(absolute_file_path) and mode & os.W_OK:
            return False
        return original_access(path, mode)

    monkeypatch.setattr(os, "access", mock_access)

    # Update the in-memory tree
    temp_workspace.build_workspace_directory_tree()

    # Attempt to remove the protected file
    with pytest.raises(PermissionError) as exc_info:
        temp_workspace.remove_file_or_folder(file_path)
    assert "Permission denied" in str(exc_info.value)