import json
import os
from pathlib import Path
import tempfile
from typing import Generator

import pytest
from pytest import MonkeyPatch

from autobyteus_server.file_explorer.file_explorer import FileExplorer
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
    assert temp_workspace.root_node.name == os.path.basename(temp_workspace.workspace_root_path)
    assert not temp_workspace.root_node.is_file


def test_read_file_content_success(temp_workspace: FileExplorer) -> None:
    """
    Test reading file content within the allowed size.
    """
    file_path = "read_test.txt"
    content = "Read this content."
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_file_path.write_text(content, encoding="utf-8")

    # Rebuild the tree so that 'read_test.txt' is tracked
    temp_workspace.build_workspace_directory_tree()

    read_content: str = temp_workspace.read_file_content(file_path)
    assert read_content == content


def test_read_file_content_exceeds_max_size(temp_workspace: FileExplorer) -> None:
    """
    Test that reading a file larger than the max allowed size raises an exception.
    """
    file_path = "large_file.txt"
    content = "A" * (1024 * 1024 + 1)  # 1MB + 1 byte
    absolute_file_path: Path = Path(temp_workspace.workspace_root_path) / file_path
    absolute_file_path.write_text(content, encoding="utf-8")

    temp_workspace.build_workspace_directory_tree()

    with pytest.raises(ValueError) as exc_info:
        temp_workspace.read_file_content(file_path, max_size=1024 * 1024)
    assert "exceeds the maximum allowed size" in str(exc_info.value)


def test_get_tree_returns_correct_tree(temp_workspace: FileExplorer) -> None:
    """
    Test retrieving the root node of the workspace directory tree.
    """
    tree = temp_workspace.get_tree()
    assert isinstance(tree, TreeNode)
    assert tree.name == os.path.basename(temp_workspace.workspace_root_path)


def test_to_json_returns_valid_json(temp_workspace: FileExplorer) -> None:
    """
    Test converting the directory tree to JSON.
    """
    json_repr: str = temp_workspace.to_json()
    if json_repr:
        tree_dict = json.loads(json_repr)
        assert "name" in tree_dict
        assert "children" in tree_dict


def test_read_file_outside_workspace_raises_error(temp_workspace: FileExplorer) -> None:
    """
    Test that reading a file outside the workspace root raises ValueError.
    """
    with pytest.raises(ValueError) as exc_info:
        temp_workspace.read_file_content("/outside.txt")
    assert "Access denied: File is outside the workspace" in str(exc_info.value)