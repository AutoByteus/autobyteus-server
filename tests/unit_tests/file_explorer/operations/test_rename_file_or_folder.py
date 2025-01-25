import os
import pytest
import tempfile
from pathlib import Path
from typing import Generator

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent, RenameChange

@pytest.fixture
def temp_workspace() -> Generator[FileExplorer, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_explorer = FileExplorer(workspace_root_path=temp_dir)
        file_explorer.build_workspace_directory_tree()
        yield file_explorer


def test_rename_file_success(temp_workspace: FileExplorer) -> None:
    file_name = "original_name.txt"
    content = "This file will be renamed."
    absolute_source_file_path: Path = Path(temp_workspace.workspace_root_path) / file_name
    absolute_source_file_path.write_text(content, encoding="utf-8")

    temp_workspace.build_workspace_directory_tree()

    new_file_name = "renamed_file.txt"
    change_event: FileSystemChangeEvent = temp_workspace.rename_file_or_folder(file_name, new_file_name)

    # Old file should not exist
    assert not absolute_source_file_path.exists()

    # The new file should exist
    absolute_renamed_file_path: Path = Path(temp_workspace.workspace_root_path) / new_file_name
    assert absolute_renamed_file_path.exists()
    assert absolute_renamed_file_path.read_text(encoding="utf-8") == content

    # Check the in-memory tree
    original_node_found = False
    renamed_node_found = False
    for child in temp_workspace.root_node.children:
        if child.name == file_name:
            original_node_found = True
        if child.name == new_file_name:
            renamed_node_found = True

    assert not original_node_found
    assert renamed_node_found

    # Verify the change event
    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 1
    rename_change = change_event.changes[0]
    assert isinstance(rename_change, RenameChange)
    assert rename_change.node.name == new_file_name
    assert rename_change.node.id != ""


def test_rename_folder_success(temp_workspace: FileExplorer) -> None:
    folder_name = "my_folder"
    file_name = "inside_file.txt"
    content = "Some content inside the folder."
    folder_path = Path(temp_workspace.workspace_root_path) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    # create a file inside that folder
    inside_file_path = folder_path / file_name
    inside_file_path.write_text(content, encoding="utf-8")

    temp_workspace.build_workspace_directory_tree()

    new_folder_name = "renamed_folder"
    change_event: FileSystemChangeEvent = temp_workspace.rename_file_or_folder(folder_name, new_folder_name)

    old_folder_path = Path(temp_workspace.workspace_root_path) / folder_name
    assert not old_folder_path.exists()

    renamed_folder_path = Path(temp_workspace.workspace_root_path) / new_folder_name
    assert renamed_folder_path.exists()
    new_inside_file_path = renamed_folder_path / file_name
    assert new_inside_file_path.exists()
    assert new_inside_file_path.read_text(encoding="utf-8") == content

    old_folder_node_found = False
    new_folder_node = None
    for child in temp_workspace.root_node.children:
        if child.name == folder_name:
            old_folder_node_found = True
        if child.name == new_folder_name:
            new_folder_node = child

    assert not old_folder_node_found
    assert new_folder_node is not None
    assert not new_folder_node.is_file

    inside_file_node_found = False
    for child in new_folder_node.children:
        if child.name == file_name:
            inside_file_node_found = True
            assert child.is_file

    assert inside_file_node_found

    # Verify the rename event
    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 1
    rename_change = change_event.changes[0]
    assert isinstance(rename_change, RenameChange)
    assert rename_change.node.name == new_folder_name
    assert rename_change.node.id == new_folder_node.id