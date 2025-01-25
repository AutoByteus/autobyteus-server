import os
import pytest
import tempfile
from pathlib import Path
from typing import Generator

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent, DeleteChange

@pytest.fixture
def temp_workspace() -> Generator[FileExplorer, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_explorer = FileExplorer(workspace_root_path=temp_dir)
        file_explorer.build_workspace_directory_tree()
        yield file_explorer

def test_remove_file_or_folder_success(temp_workspace: FileExplorer) -> None:
    file_path = "remove_test.txt"
    content = "To be removed."
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.write_text(content, encoding="utf-8")

    temp_workspace.build_workspace_directory_tree()
    change_event: FileSystemChangeEvent = temp_workspace.remove_file_or_folder(file_path)

    assert not absolute_file_path.exists()
    assert isinstance(change_event, FileSystemChangeEvent)
    assert len(change_event.changes) == 1
    delete_change = change_event.changes[0]
    assert isinstance(delete_change, DeleteChange)


def test_remove_nonexistent_file_raises_error(temp_workspace: FileExplorer) -> None:
    with pytest.raises(ValueError) as exc_info:
        temp_workspace.remove_file_or_folder("nonexistent.txt")
    assert "Path not found" in str(exc_info.value)


def test_remove_file_without_permission(temp_workspace: FileExplorer, monkeypatch: pytest.MonkeyPatch) -> None:
    file_path = "protected_remove.txt"
    content = "Cannot remove this file."
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
        temp_workspace.remove_file_or_folder(file_path)
    assert "Permission denied" in str(exc_info.value)