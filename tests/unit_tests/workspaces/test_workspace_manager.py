"""
This module provides tests for the WorkspaceManager.
"""

import os
import tempfile
import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from autobyteus_server.workspaces.workspace import Workspace
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.workspaces.workspace_tools.command_executor import CommandExecutor, CommandExecutionResult


@pytest.fixture
def temp_workspace():
    """
    Fixture to create and clean up a temporary workspace directory.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_dir)


def test_should_add_workspace_successfully(temp_workspace):
    """
    Test the add_workspace method of WorkspaceManager should add workspace successfully.
    """
    # Arrange
    os.mkdir(os.path.join(temp_workspace, 'test_directory'))  # Create a subdirectory in the temporary directory
    manager = WorkspaceManager()

    # Act
    workspace = manager.add_workspace(temp_workspace)

    # Assert
    assert workspace.name == os.path.basename(temp_workspace)
    assert workspace.root_path == temp_workspace
    assert isinstance(manager.get_workspace_by_root_path(temp_workspace), Workspace)
    # Assuming Workspace has a file_explorer attribute with a tree structure
    assert len(workspace.file_explorer.children) == 1  # As we have created one subdirectory
    assert workspace.file_explorer.children[0].name == 'test_directory'


def test_should_retrieve_workspace(temp_workspace):
    """
    Test the get_workspace_by_root_path method of WorkspaceManager should retrieve workspace correctly.
    """
    # Arrange
    manager = WorkspaceManager()
    manager.add_workspace(temp_workspace)

    # Act
    workspace = manager.get_workspace_by_root_path(temp_workspace)

    # Assert
    assert isinstance(workspace, Workspace)
    assert workspace.root_path == temp_workspace


@pytest.mark.asyncio
async def test_execute_command_success(temp_workspace):
    """
    Test the CommandExecutor.execute_command method for successful command execution.
    """
    # Arrange
    manager = WorkspaceManager()
    workspace = manager.add_workspace(temp_workspace)
    executor = CommandExecutor(workspace_root_path=temp_workspace)

    with patch('autobyteus.tools.bash.bash_executor.BashExecutor.execute', new=AsyncMock(return_value="Command executed successfully")):
        # Act
        result = await executor.execute_command("echo 'Hello, World!'")

    # Assert
    assert isinstance(result, CommandExecutionResult)
    assert result.success is True
    assert result.message == "Command executed successfully"


@pytest.mark.asyncio
async def test_execute_command_failure(temp_workspace):
    """
    Test the CommandExecutor.execute_command method for failed command execution.
    """
    # Arrange
    manager = WorkspaceManager()
    workspace = manager.add_workspace(temp_workspace)
    executor = CommandExecutor(workspace_root_path=temp_workspace)

    with patch('autobyteus.tools.bash.bash_executor.BashExecutor.execute', new=AsyncMock(side_effect=subprocess.CalledProcessError(returncode=1, cmd="invalid_command", stderr="command not found"))):
        # Act
        result = await executor.execute_command("invalid_command")

    # Assert
    assert isinstance(result, CommandExecutionResult)
    assert result.success is False
    assert "Command execution failed with return code 1: command not found" in result.message


@pytest.mark.asyncio
async def test_execute_command_unexpected_error(temp_workspace):
    """
    Test the CommandExecutor.execute_command method for unexpected errors.
    """
    # Arrange
    manager = WorkspaceManager()
    workspace = manager.add_workspace(temp_workspace)
    executor = CommandExecutor(workspace_root_path=temp_workspace)

    with patch('autobyteus.tools.bash.bash_executor.BashExecutor.execute', new=AsyncMock(side_effect=Exception("Unexpected Error"))):
        # Act
        result = await executor.execute_command("echo 'Test'")

    # Assert
    assert isinstance(result, CommandExecutionResult)
    assert result.success is False
    assert "An unexpected error occurred during command execution: Unexpected Error" in result.message