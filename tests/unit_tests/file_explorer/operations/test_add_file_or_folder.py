import os
import pytest
import tempfile
from pathlib import Path
from typing import Generator

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent, AddChange

@pytest.fixture
def temp_workspace() -> Generator[FileExplorer, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_explorer = FileExplorer(workspace_root_path=temp_dir)
        file_explorer.build_workspace_directory_tree()
        yield file_explorer

def test_add_file_success(temp_workspace: FileExplorer) -> None:
    file_path = "new_file.txt"
    change_event: FileSystemChangeEvent = temp_workspace.add_file_or_folder(file_path, is_file=True)

    absolute_file_path = Path(temp_workspace.workspace_root_path) / file_path
    assert absolute_file_path.exists()
    assert absolute_file_path.is_file()

    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 1
    add_change = change_event.changes[0]
    assert isinstance(add_change, AddChange)
    assert add_change.node.name == "new_file.txt"

def test_add_folder_success(temp_workspace: FileExplorer) -> None:
    folder_path = "new_folder"
    change_event: FileSystemChangeEvent = temp_workspace.add_file_or_folder(folder_path, is_file=False)

    absolute_folder_path = Path(temp_workspace.workspace_root_path) / folder_path
    assert absolute_folder_path.exists()
    assert absolute_folder_path.is_dir()

    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 1
    add_change = change_event.changes[0]
    assert isinstance(add_change, AddChange)
    assert add_change.node.name == "new_folder"

def test_add_nested_folder_creates_all_parents(temp_workspace: FileExplorer) -> None:
    nested_folder_path = "level1/level2/level3"
    change_event: FileSystemChangeEvent = temp_workspace.add_file_or_folder(nested_folder_path, is_file=False)

    absolute_folder_path = Path(temp_workspace.workspace_root_path) / nested_folder_path
    assert absolute_folder_path.exists()
    assert absolute_folder_path.is_dir()

    # Ensure multiple AddChange entries exist (each subfolder added)
    assert isinstance(change_event, FileSystemChangeEvent)
    # 3 subfolders => 3 AddChanges
    assert len(change_event.changes) == 3
    for change in change_event.changes:
        assert isinstance(change, AddChange)
