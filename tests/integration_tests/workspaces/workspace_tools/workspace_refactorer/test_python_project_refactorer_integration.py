import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.workspaces.workspace import Workspace
from autobyteus_server.workspaces.workspace_tools.workspace_refactorer.python_project_refactorer import PythonProjectRefactorer


@pytest.fixture
def mock_workspace():
    with tempfile.TemporaryDirectory() as tmpdirname:
        src_dir = os.path.join(tmpdirname, 'src')
        os.makedirs(src_dir)
        
        # Create a Python file with a function without a docstring
        code = """
def add(a, b):
    return a + b
"""
        file_path = os.path.join(src_dir, 'math_utils.py')
        with open(file_path, 'w') as f:
            f.write(code)
        
        # Create __init__.py file
        init_path = os.path.join(src_dir, '__init__.py')
        with open(init_path, 'w') as f:
            f.write("# init file")
        
        file_explorer = FileExplorer(tmpdirname)
        workspace = Workspace(root_path=tmpdirname, file_explorer=file_explorer)
        
        yield workspace


@patch('autobyteus_server.workspaces.workspace_tools.workspace_refactorer.python_project_refactorer.PythonProjectRefactorer.llm_integration')
def test_refactor_process(mock_llm, mock_workspace, capsys):
    # Mock LLM response
    mock_llm.process_input_messages.return_value = '''
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b
'''
    
    refactorer = PythonProjectRefactorer(mock_workspace)
    refactorer.refactor()
    
    captured = capsys.readouterr()
    
    # Check if the refactored code is logged
    assert "def add(a: int, b: int) -> int:" in captured.out
    assert '"""Add two integers and return the sum."""' in captured.out
    
    # Ensure __init__.py was not processed
    assert "__init__.py" not in captured.out


def test_construct_prompt(mock_workspace):
    refactorer = PythonProjectRefactorer(mock_workspace)
    file_path = os.path.join(mock_workspace.root_path, 'src', 'math_utils.py')
    
    prompt = refactorer.construct_prompt(file_path)
    
    assert f"Please examine the source code in file {file_path}" in prompt
    assert "def add(a, b):" in prompt
    assert "return a + b" in prompt