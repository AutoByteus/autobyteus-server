import os
import pytest
import tempfile
from pathlib import Path
from typing import Generator

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent, MoveChange

@pytest.fixture
def temp_workspace() -> Generator[FileExplorer, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_explorer = FileExplorer(workspace_root_path=temp_dir)
        file_explorer.build_workspace_directory_tree()
        yield file_explorer

def test_move_file_or_folder_success(temp_workspace: FileExplorer) -> None:
    source_folder = "folder_a"
    source_file_name = "test_file.txt"
    source_path = os.path.join(source_folder, source_file_name)
    content = "This file will be moved."

    absolute_source_file_path: Path = Path(temp_workspace.workspace_root_path) / source_path
    absolute_source_file_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_source_file_path.write_text(content, encoding="utf-8")

    destination_folder = "folder_b"
    absolute_destination_folder_path: Path = Path(temp_workspace.workspace_root_path) / destination_folder
    absolute_destination_folder_path.mkdir(parents=True, exist_ok=True)

    temp_workspace.build_workspace_directory_tree()
    change_event: FileSystemChangeEvent = temp_workspace.move_file_or_folder(source_path, destination_folder)

    new_file_location: Path = absolute_destination_folder_path / source_file_name
    assert new_file_location.exists()
    assert new_file_location.read_text(encoding="utf-8") == content
    assert not absolute_source_file_path.exists()

    folder_a_node = None
    folder_b_node = None
    for child in temp_workspace.root_node.children:
        if child.name == "folder_a":
            folder_a_node = child
        if child.name == "folder_b":
            folder_b_node = child

    assert folder_a_node is not None
    assert folder_b_node is not None

    # Verify that the source file was removed from folder_a
    for child in folder_a_node.children:
        assert child.name != source_file_name

    # Verify that the moved file is now under folder_b
    moved_file_node = None
    for child in folder_b_node.children:
        if child.name == source_file_name:
            moved_file_node = child

    assert moved_file_node is not None
    assert moved_file_node.is_file

    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 1
    move_change = change_event.changes[0]
    assert isinstance(move_change, MoveChange)
    assert move_change.node.name == source_file_name
    assert move_change.old_parent_id == folder_a_node.id
    assert move_change.new_parent_id == folder_b_node.id