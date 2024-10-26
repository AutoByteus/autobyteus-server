"""
Unit tests for the command executor module.
"""
import pytest
import tempfile
from unittest.mock import Mock, patch
from autobyteus_server.workspaces.workspace_tools.command_executor import (
    CommandExecutor,
    CommandExecutionResult
)

# General Fixtures
@pytest.fixture
def temp_workspace():
    """
    Fixture providing a temporary workspace directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def workspace_path():
    """
    Fixture providing a fixed workspace path for testing.
    """
    return "/test/workspace/path"

# Command Executor Specific Fixtures
@pytest.fixture
def mock_bash_executor():
    """Fixture providing a mock bash executor."""
    with patch('autobyteus_server.workspaces.workspace_tools.command_executor.BashExecutor') as mock:
        executor = Mock()
        mock.return_value = executor
        yield executor

@pytest.fixture
def command_executor(mock_bash_executor):
    """Fixture providing a CommandExecutor instance with mocked bash executor."""
    return CommandExecutor("/test/workspace/path")


class TestCommandExecutionResult:
    """Test cases for CommandExecutionResult dataclass."""

    def test_successful_result_creation(self):
        """Test creating a successful execution result."""
        result = CommandExecutionResult(success=True, message="Command executed successfully")
        
        assert result.success is True
        assert result.message == "Command executed successfully"

    def test_failed_result_creation(self):
        """Test creating a failed execution result."""
        result = CommandExecutionResult(success=False, message="Command failed")
        
        assert result.success is False
        assert result.message == "Command failed"


class TestCommandExecutor:
    """Test cases for CommandExecutor class."""

    def test_initialization(self):
        """Test proper initialization of CommandExecutor."""
        executor = CommandExecutor("/test/path")
        
        assert executor.workspace_root_path == "/test/path"
        assert executor.bash_executor is not None

    def test_successful_command_execution(self, command_executor, mock_bash_executor):
        """Test successful command execution."""
        # Arrange
        mock_bash_executor.execute.return_value = "command output"
        
        # Act
        result = command_executor.execute_command("test command")
        
        # Assert
        assert result.success is True
        assert result.message == "command output"
        mock_bash_executor.execute.assert_called_once_with(
            command="cd /test/workspace/path && test command"
        )

    def test_failed_command_execution(self, command_executor, mock_bash_executor):
        """Test command execution with raised exception."""
        # Arrange
        mock_bash_executor.execute.side_effect = Exception("Command failed")
        
        # Act
        result = command_executor.execute_command("test command")
        
        # Assert
        assert result.success is False
        assert "Command execution failed: Command failed" in result.message

    @pytest.mark.parametrize("command,expected_full_command", [
        ("ls", "cd /test/workspace/path && ls"),
        ("pwd", "cd /test/workspace/path && pwd"),
        ("echo 'test'", "cd /test/workspace/path && echo 'test'"),
    ])
    def test_workspace_path_prepending(
        self, command_executor, mock_bash_executor, command, expected_full_command
    ):
        """Test proper workspace path handling for different commands."""
        # Arrange
        mock_bash_executor.execute.return_value = "success"
        
        # Act
        command_executor.execute_command(command)
        
        # Assert
        mock_bash_executor.execute.assert_called_once_with(command=expected_full_command)

    def test_empty_command_handling(self, command_executor, mock_bash_executor):
        """Test handling of empty command."""
        # Arrange
        mock_bash_executor.execute.return_value = ""
        
        # Act
        result = command_executor.execute_command("")
        
        # Assert
        assert result.success is True
        assert result.message == ""
        mock_bash_executor.execute.assert_called_once_with(
            command="cd /test/workspace/path && "
        )

    def test_real_workspace_path(self, temp_workspace):
        """Test with a real temporary workspace directory."""
        # Arrange
        executor = CommandExecutor(temp_workspace)
        
        # Act & Assert
        assert executor.workspace_root_path == temp_workspace