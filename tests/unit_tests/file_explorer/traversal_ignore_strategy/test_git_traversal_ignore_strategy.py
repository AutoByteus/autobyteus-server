# tests/unit_tests/file_explorer/test_traversal_ignore_strategy.py

import os
import pytest
import tempfile
from autobyteus_server.file_explorer.traversal_ignore_strategy.git_ignore_strategy import GitIgnoreStrategy


@pytest.fixture
def temp_dir():
    """
    Pytest fixture to create a temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname  # Provide the fixture value


def write_gitignore(tmpdirname: str, content: str):
    """
    Helper function to write content to a .gitignore file.
    """
    gitignore_path = os.path.join(tmpdirname, '.gitignore')
    with open(gitignore_path, 'w') as f:
        f.write(content)


def test_git_ignore_strategy_ignore_matched_pattern(temp_dir):
    """
    Test that GitIgnoreStrategy correctly ignores files matching the pattern.
    """
    # Arrange
    write_gitignore(temp_dir, '*.txt\n')
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act
    should_ignore = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'test.txt'))

    # Assert
    assert should_ignore is True, "Expected 'test.txt' to be ignored based on '*.txt' pattern"


def test_git_ignore_strategy_not_ignore_unmatched_pattern(temp_dir):
    """
    Test that GitIgnoreStrategy does not ignore files not matching the pattern.
    """
    # Arrange
    write_gitignore(temp_dir, '*.txt\n')
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act
    should_ignore = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'test.py'))

    # Assert
    assert should_ignore is False, "Expected 'test.py' not to be ignored as it does not match '*.txt'"


def test_git_ignore_strategy_not_ignore_no_gitignore_file(temp_dir):
    """
    Test that GitIgnoreStrategy does not ignore any files when no .gitignore file is present.
    """
    # Arrange
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act
    should_ignore = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'test.txt'))

    # Assert
    assert should_ignore is False, "Expected 'test.txt' not to be ignored as no .gitignore file is present"


def test_git_ignore_strategy_ignore_specific_folder(temp_dir):
    """
    Test that GitIgnoreStrategy correctly ignores a specified folder.
    """
    # Arrange
    write_gitignore(temp_dir, 'folder/\n')
    # Create 'folder' as a directory
    folder_path = os.path.join(temp_dir, 'folder')
    os.makedirs(folder_path, exist_ok=True)
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act
    should_ignore = git_ignore_strategy.should_ignore(folder_path)

    # Assert
    assert should_ignore is True, "Expected 'folder' to be ignored based on 'folder/' pattern"


def test_git_ignore_strategy_ignore_files_in_ignored_folder(temp_dir):
    """
    Test that GitIgnoreStrategy ignores files within an ignored folder.
    """
    # Arrange
    write_gitignore(temp_dir, 'folder/\n')
    # Create 'folder' as a directory
    folder_path = os.path.join(temp_dir, 'folder')
    os.makedirs(folder_path, exist_ok=True)
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act
    should_ignore = git_ignore_strategy.should_ignore(os.path.join(folder_path, 'file.txt'))

    # Assert
    assert should_ignore is True, "Expected 'folder/file.txt' to be ignored as 'folder/' is ignored"


def test_git_ignore_strategy_handle_negation_pattern(temp_dir):
    """
    Test that GitIgnoreStrategy handles negation patterns correctly.
    """
    # Arrange
    gitignore_content = """
# Ignore all .log files
*.log

# But do not ignore important.log
!important.log
"""
    write_gitignore(temp_dir, gitignore_content)
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act & Assert
    ignored_file = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'debug.log'))
    not_ignored_file = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'important.log'))

    assert ignored_file is True, "Expected 'debug.log' to be ignored based on '*.log' pattern"
    assert not_ignored_file is False, "Expected 'important.log' not to be ignored due to '!important.log' pattern"


def test_git_ignore_strategy_ignore_nested_gitignore_patterns(temp_dir):
    """
    Test that GitIgnoreStrategy correctly handles nested .gitignore patterns.
    """
    # Arrange
    # Root .gitignore ignores *.pyc files
    write_gitignore(temp_dir, '*.pyc\n')
    # Create a subdirectory with its own .gitignore that ignores *.log
    sub_dir = os.path.join(temp_dir, 'subdir')
    os.makedirs(sub_dir, exist_ok=True)
    write_gitignore(sub_dir, '*.log\n')
    git_ignore_strategy_root = GitIgnoreStrategy(temp_dir)
    git_ignore_strategy_sub = GitIgnoreStrategy(sub_dir)

    # Act
    ignore_root_pycache = git_ignore_strategy_root.should_ignore(os.path.join(temp_dir, 'file.pyc'))
    ignore_subdir_log = git_ignore_strategy_sub.should_ignore(os.path.join(sub_dir, 'app.log'))
    not_ignore_subdir_py = git_ignore_strategy_sub.should_ignore(os.path.join(sub_dir, 'app.py'))

    # Assert
    assert ignore_root_pycache is True, "Expected 'file.pyc' to be ignored based on root '*.pyc' pattern"
    assert ignore_subdir_log is True, "Expected 'subdir/app.log' to be ignored based on subdir '*.log' pattern"
    assert not_ignore_subdir_py is False, "Expected 'subdir/app.py' not to be ignored as it does not match '*.log'"


def test_git_ignore_strategy_ignore_multiple_patterns(temp_dir):
    """
    Test that GitIgnoreStrategy correctly ignores files based on multiple patterns.
    """
    # Arrange
    gitignore_content = """
# Ignore all txt and log files
*.txt
*.log
"""
    write_gitignore(temp_dir, gitignore_content)
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act & Assert
    ignore_txt = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'notes.txt'))
    ignore_log = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'debug.log'))
    not_ignore_md = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'README.md'))

    assert ignore_txt is True, "Expected 'notes.txt' to be ignored based on '*.txt' pattern"
    assert ignore_log is True, "Expected 'debug.log' to be ignored based on '*.log' pattern"
    assert not_ignore_md is False, "Expected 'README.md' not to be ignored as it does not match any pattern"


def test_git_ignore_strategy_ignore_partial_matches(temp_dir):
    """
    Test that GitIgnoreStrategy does not ignore files that partially match patterns.
    """
    # Arrange
    write_gitignore(temp_dir, '*.txt\n')
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act
    should_ignore = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'my_test.txt_backup'))

    # Assert
    assert should_ignore is False, "Expected 'my_test.txt_backup' not to be ignored as it does not fully match '*.txt'"


def test_git_ignore_strategy_ignore_with_subdirectories(temp_dir):
    """
    Test that GitIgnoreStrategy correctly ignores files within subdirectories based on patterns.
    """
    # Arrange
    gitignore_content = """
# Ignore all .env files in any subdirectory
**/.env
"""
    write_gitignore(temp_dir, gitignore_content)
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Create 'config' subdirectory
    config_dir = os.path.join(temp_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)

    # Act & Assert
    ignore_env_root = git_ignore_strategy.should_ignore(os.path.join(temp_dir, '.env'))
    ignore_env_sub = git_ignore_strategy.should_ignore(os.path.join(config_dir, '.env'))
    not_ignore_env_other = git_ignore_strategy.should_ignore(os.path.join(config_dir, 'settings.env'))

    assert ignore_env_root is True, "Expected '.env' in root to be ignored based on '**/.env' pattern"
    assert ignore_env_sub is True, "Expected 'config/.env' to be ignored based on '**/.env' pattern"
    assert not_ignore_env_other is False, "Expected 'config/settings.env' not to be ignored as it does not match '**/.env'"


def test_git_ignore_strategy_ignore_files_with_slash_pattern(temp_dir):
    """
    Test that GitIgnoreStrategy correctly ignores directories when patterns include slashes.
    """
    # Arrange
    gitignore_content = """
/specific_folder/
"""
    write_gitignore(temp_dir, gitignore_content)
    # Create 'specific_folder' as a directory
    specific_folder = os.path.join(temp_dir, 'specific_folder')
    os.makedirs(specific_folder, exist_ok=True)
    # Create 'other_folder' as a directory
    other_folder = os.path.join(temp_dir, 'other_folder')
    os.makedirs(other_folder, exist_ok=True)
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act & Assert
    ignore_specific_folder = git_ignore_strategy.should_ignore(specific_folder)
    ignore_other_folder = git_ignore_strategy.should_ignore(other_folder)

    assert ignore_specific_folder is True, "Expected 'specific_folder' to be ignored based on '/specific_folder/' pattern"
    assert ignore_other_folder is False, "Expected 'other_folder' not to be ignored as it does not match the pattern"


def test_git_ignore_strategy_ignore_files_with_extension_pattern(temp_dir):
    """
    Test that GitIgnoreStrategy correctly ignores files based on extension patterns.
    """
    # Arrange
    gitignore_content = """
*.md
*.pyc
"""
    write_gitignore(temp_dir, gitignore_content)
    git_ignore_strategy = GitIgnoreStrategy(temp_dir)

    # Act & Assert
    ignore_md = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'README.md'))
    ignore_pyc = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'module.pyc'))
    not_ignore_py = git_ignore_strategy.should_ignore(os.path.join(temp_dir, 'script.py'))

    assert ignore_md is True, "Expected 'README.md' to be ignored based on '*.md' pattern"
    assert ignore_pyc is True, "Expected 'module.pyc' to be ignored based on '*.pyc' pattern"
    assert not_ignore_py is False, "Expected 'script.py' not to be ignored as it does not match any pattern"
