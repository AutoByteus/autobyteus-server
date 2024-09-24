"""
This module provides tests for the WorkspaceManager.
"""

import os
import tempfile
from autobyteus_server.workspaces.workspace import Workspace
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

def test_should_add_workspace_successfully():
    """
    Test the add_workspace method of WorkspaceManager should add workspace successfully.
    """
    # Arrange
    temp_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(temp_dir, 'test_directory'))  # Create a subdirectory in the temporary directory
    manager = WorkspaceManager()

    # Act
    tree = manager.add_workspace(temp_dir)

    # Assert
    assert tree.name == os.path.basename(temp_dir)
    assert tree.path == temp_dir
    assert tree.is_file == False
    assert isinstance(manager.get_workspace(temp_dir), Workspace)
    assert len(tree.children) == 1  # As we have created one subdirectory
    assert tree.children[0].name == 'test_directory'

def test_should_retrieve_workspace():
    """
    Test the get_workspace method of WorkspaceManager should retrieve workspace correctly.
    """
    # Arrange
    temp_dir = tempfile.mkdtemp()
    manager = WorkspaceManager()
    manager.add_workspace(temp_dir)

    # Act
    workspace = manager.get_workspace(temp_dir)

    # Assert
    assert isinstance(workspace, Workspace)
    assert workspace.root_path == temp_dir