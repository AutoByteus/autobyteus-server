"""
Integration tests for the CommandExecutor module.
"""

import pytest
import tempfile
import os
from autobyteus_server.workspaces.workspace_tools.command_executor import CommandExecutor, CommandExecutionResult
from unittest import mock


@pytest.fixture
def real_workspace():
    """
    Fixture providing a real temporary workspace directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def command_executor(real_workspace):
    """
    Fixture providing a CommandExecutor instance with a real workspace.
    """
    return CommandExecutor(real_workspace)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_ls(command_executor, real_workspace):
    """
    Test executing the 'ls' command in the real workspace.
    """
    # Arrange
    # Create some files in the workspace
    filenames = ['file1.txt', 'file2.txt', 'script.sh']
    for filename in filenames:
        with open(os.path.join(real_workspace, filename), 'w') as f:
            f.write(f"Content of {filename}")

    # Act
    result = await command_executor.execute_command("ls")

    # Assert
    assert result.success is True
    output_files = result.message.strip().split('\n')
    assert set(output_files) == set(filenames)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_pwd(command_executor, real_workspace):
    """
    Test executing the 'pwd' command to verify the workspace path.
    """
    # Act
    result = await command_executor.execute_command("pwd")

    # Assert
    assert result.success is True
    assert result.message.strip() == real_workspace


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_echo(command_executor):
    """
    Test executing the 'echo' command.
    """
    # Act
    test_message = "Hello, Integration Test!"
    result = await command_executor.execute_command(f"echo '{test_message}'")

    # Assert
    assert result.success is True
    assert result.message.strip() == test_message


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_invalid_command(command_executor):
    """
    Test executing an invalid command to ensure proper error handling.
    """
    # Act
    result = await command_executor.execute_command("invalid_command_xyz")

    # Assert
    assert result.success is False
    assert "Command execution failed" in result.message


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_touch(command_executor, real_workspace):
    """
    Test executing the 'touch' command to create a new file.
    """
    # Arrange
    new_file = "new_file.txt"

    # Act
    result = await command_executor.execute_command(f"touch {new_file}")

    # Assert
    assert result.success is True
    assert os.path.isfile(os.path.join(real_workspace, new_file))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_rm(command_executor, real_workspace):
    """
    Test executing the 'rm' command to delete a file.
    """
    # Arrange
    file_to_delete = "delete_me.txt"
    file_path = os.path.join(real_workspace, file_to_delete)
    with open(file_path, 'w') as f:
        f.write("This file will be deleted.")

    assert os.path.isfile(file_path)

    # Act
    result = await command_executor.execute_command(f"rm {file_to_delete}")

    # Assert
    assert result.success is True
    assert not os.path.isfile(file_path)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_command_with_spaces_in_path(real_workspace):
    """
    Test executing a command when the workspace path contains spaces.
    """
    with tempfile.TemporaryDirectory(prefix="workspace with spaces ") as temp_dir:
        command_executor_with_spaces = CommandExecutor(temp_dir)
        new_file = "space_test.txt"

        result = await command_executor_with_spaces.execute_command(f"touch {new_file}")
        assert result.success is True
        assert os.path.isfile(os.path.join(temp_dir, new_file))