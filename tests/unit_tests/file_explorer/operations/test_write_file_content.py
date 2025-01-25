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


def test_write_file_content_creates_file_and_updates_tree(temp_workspace: FileExplorer) -> None:
    file_path = "test_folder/test_file.txt"
    content = "Hello, World!"

    change_event: FileSystemChangeEvent = temp_workspace.write_file_content(file_path, content)

    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    assert absolute_file_path.exists()
    assert absolute_file_path.read_text(encoding="utf-8") == content

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
    assert isinstance(change_event, FileSystemChangeEvent)
    # 1 directory + 1 file creation => 2 changes
    assert len(change_event.changes) == 2
    add_changes = [change for change in change_event.changes if isinstance(change, AddChange)]
    assert len(add_changes) == 2


def test_write_file_outside_workspace_raises_error(temp_workspace: FileExplorer) -> None:
    with pytest.raises(ValueError) as exc_info:
        temp_workspace.write_file_content("/outside.txt", "Should fail.")
    assert "The path must be relative to the workspace root" in str(exc_info.value)


def test_write_file_without_permission(temp_workspace: FileExplorer, monkeypatch: pytest.MonkeyPatch) -> None:
    file_path = "protected.txt"
    content = "Cannot write to this file."
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.write_text(content, encoding="utf-8")

    original_access = os.access

    def mock_access(path: str, mode: int) -> bool:
        if path == str(absolute_file_path) and mode & os.W_OK:
            return False
        return original_access(path, mode)

    monkeypatch.setattr(os, "access", mock_access)
    temp_workspace.build_workspace_directory_tree()

    with pytest.raises(PermissionError) as exc_info:
        temp_workspace.write_file_content(file_path, "New content.")
    assert "Permission denied" in str(exc_info.value)