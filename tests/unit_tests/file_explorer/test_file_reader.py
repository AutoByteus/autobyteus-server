# File: autobyteus-server/tests/unit_tests/file_explorer/test_file_reader.py

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open
from autobyteus_server.file_explorer.file_reader import FileReader

@pytest.fixture
def temp_python_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write("print('Hello, World!')")
        temp_file_path = temp_file.name
    yield temp_file_path
    os.unlink(temp_file_path)

@pytest.fixture
def temp_non_python_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("This is a text file.")
        temp_file_path = temp_file.name
    yield temp_file_path
    os.unlink(temp_file_path)

def test_read_existing_python_file(temp_python_file):
    content = FileReader.read_file(temp_python_file)
    assert content == "print('Hello, World!')"

def test_read_non_existent_file():
    content = FileReader.read_file('non_existent_file.py')
    assert content is None

def test_read_non_python_file(temp_non_python_file):
    content = FileReader.read_file(temp_non_python_file)
    assert content is None

@pytest.mark.parametrize("error, expected", [
    (UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte'), None),
    (PermissionError(), None)
])
def test_read_file_with_errors(error, expected):
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = error
        content = FileReader.read_file('test_file.py')
        assert content == expected

def test_read_file_with_different_encodings():
    test_content = "print('Hello, 世界!')"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', encoding='utf-8', delete=False) as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name

    try:
        content = FileReader.read_file(temp_file_path)
        assert content == test_content
    finally:
        os.unlink(temp_file_path)