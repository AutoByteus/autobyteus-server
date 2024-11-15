# tests/unit_tests/file_explorer/sort_strategy/test_default_sort_strategy.py

import os
import pytest
import tempfile
from autobyteus_server.file_explorer.sort_strategy.default_sort_strategy import DefaultSortStrategy


@pytest.fixture
def sort_strategy() -> DefaultSortStrategy:
    """Fixture to provide an instance of DefaultSortStrategy."""
    return DefaultSortStrategy()


@pytest.fixture
def setup_files_and_folders():
    """
    Creates a temporary directory structure with a mix of hidden and normal files and folders.
    
    Structure:
    /tmp_dir/
        .dot_dir/
            nested_dir/
            .nested_dot_dir/
            .nested_dot_file
            nested_file
        normal_dir/
            .nested_dot_dir/
            nested_dir/
            .nested_dot_file
            nested_file
        .dot_file
        normal_file
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create directories
        os.makedirs(os.path.join(tmp_dir, '.dot_dir', 'nested_dir'))
        os.makedirs(os.path.join(tmp_dir, '.dot_dir', '.nested_dot_dir'))
        os.makedirs(os.path.join(tmp_dir, 'normal_dir', 'nested_dir'))
        os.makedirs(os.path.join(tmp_dir, 'normal_dir', '.nested_dot_dir'))
        
        # Create files
        with open(os.path.join(tmp_dir, '.dot_file'), 'w') as f:
            f.write('dot file')
        with open(os.path.join(tmp_dir, 'normal_file'), 'w') as f:
            f.write('normal file')
        with open(os.path.join(tmp_dir, '.dot_dir', 'nested_file'), 'w') as f:
            f.write('nested file')
        with open(os.path.join(tmp_dir, '.dot_dir', '.nested_dot_file'), 'w') as f:
            f.write('nested dot file')
        with open(os.path.join(tmp_dir, 'normal_dir', 'nested_file'), 'w') as f:
            f.write('nested file')
        with open(os.path.join(tmp_dir, 'normal_dir', '.nested_dot_file'), 'w') as f:
            f.write('nested dot file')
    
        yield tmp_dir  # Provide the path to the temporary directory


def test_sorts_folders_and_files_correctly(sort_strategy: DefaultSortStrategy, setup_files_and_folders):
    """
    Tests that folders are sorted before files and both are sorted alphabetically, including hidden entries.
    """
    # Arrange
    root_dir = setup_files_and_folders
    paths = [os.path.join(root_dir, path_name) 
             for path_name in os.listdir(root_dir)]
    
    # Act
    sorted_paths = sort_strategy.sort(paths)
    
    # Assert
    expected_order = sorted(
        [path for path in paths if os.path.isdir(path)],
        key=lambda x: os.path.basename(x).lower()
    ) + sorted(
        [path for path in paths if os.path.isfile(path)],
        key=lambda x: os.path.basename(x).lower()
    )
    
    assert sorted_paths == expected_order, "Sorting at root level failed."


def test_sorts_nested_folders_and_files_correctly(sort_strategy: DefaultSortStrategy, setup_files_and_folders):
    """
    Tests that nested folders and files within both hidden and normal directories are sorted correctly.
    """
    # Arrange
    root_dir = setup_files_and_folders
    
    # Define subdirectories to test
    subdirs = ['.dot_dir', 'normal_dir']
    
    for subdir in subdirs:
        current_dir = os.path.join(root_dir, subdir)
        child_paths = [os.path.join(current_dir, path_name) 
                      for path_name in os.listdir(current_dir)]
        
        # Act
        sorted_child_paths = sort_strategy.sort(child_paths)
        
        # Assert
        expected_order = sorted(
            [path for path in child_paths if os.path.isdir(path)],
            key=lambda x: os.path.basename(x).lower()
        ) + sorted(
            [path for path in child_paths if os.path.isfile(path)],
            key=lambda x: os.path.basename(x).lower()
        )
        
        assert sorted_child_paths == expected_order, f"Sorting in '{subdir}' failed."


@pytest.fixture
def create_test_directory_structure(tmp_path):
    """
    Creates a temporary directory structure with specified folders and files.
    
    Structure:
    /tmp_path/
        src/
        .vscode/
        public/
        README.md
        codegen.yml
        graphql.schema.json
        index.html
        package-lock.json
        package.json
        tsconfig.json
        tsconfig.node.json
        vite.config.ts
        yarn.lock
        .gitignore
    """
    directories = ['src', '.vscode', 'public']
    files = [
        'README.md', 'codegen.yml', 'graphql.schema.json', 'index.html',
        'package-lock.json', 'package.json', 'tsconfig.json',
        'tsconfig.node.json', 'vite.config.ts', 'yarn.lock', '.gitignore'
    ]

    for directory in directories:
        (tmp_path / directory).mkdir()
    
    for file in files:
        (tmp_path / file).touch()
    
    return tmp_path  # Return the base path


def test_default_sort_strategy(create_test_directory_structure, sort_strategy: DefaultSortStrategy):
    """
    Tests the DefaultSortStrategy with a predefined directory and file structure.
    """
    # Arrange
    base_path = create_test_directory_structure
    unsorted_paths = [str(base_path / path_name) 
                     for path_name in os.listdir(base_path)]
    
    # Act
    sorted_paths = sort_strategy.sort(unsorted_paths)
    
    # Assert
    # Define expected order: directories first (sorted), then files (sorted)
    expected_dirs = sorted(
        [path for path in unsorted_paths if os.path.isdir(path)],
        key=lambda x: os.path.basename(x).lower()
    )
    expected_files = sorted(
        [path for path in unsorted_paths if os.path.isfile(path)],
        key=lambda x: os.path.basename(x).lower()
    )
    expected_order = expected_dirs + expected_files
    
    assert sorted_paths == expected_order, f"Expected order is {expected_order}, but got {sorted_paths}"
