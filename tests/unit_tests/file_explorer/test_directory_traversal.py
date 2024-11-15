import pytest
import os
from pathlib import Path
from typing import List

# Import the necessary classes from your codebase
from autobyteus_server.file_explorer.directory_traversal import DirectoryTraversal
from autobyteus_server.file_explorer.tree_node import TreeNode
from autobyteus_server.file_explorer.traversal_ignore_strategy.dot_ignore_strategy import DotIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.specific_folder_ignore_strategy import SpecificFolderIgnoreStrategy
from autobyteus_server.file_explorer.sort_strategy.default_sort_strategy import DefaultSortStrategy


@pytest.fixture
def setup_basic_directory(tmp_path):
    """
    Sets up a basic directory structure:
    /A
        /B
        /C
        /D
        f.txt
        g.txt
        h.txt
    """
    A = tmp_path / "A"
    A.mkdir()
    # Create subdirectories
    for folder in ["B", "C", "D"]:
        (A / folder).mkdir()
    # Create files
    for file in ["f", "g", "h"]:
        (A / f"{file}.txt").touch()
    return A


@pytest.fixture
def setup_nested_gitignore(tmp_path):
    """
    Sets up a directory structure with nested .gitignore files:
    /A
        .gitignore (ignore 'g.txt')
        /B
            .gitignore (ignore 'b2.txt')
            /B1
                b1.txt
                b2.txt
        /C
            c1.txt
            c2.txt
        f.txt
        g.txt
    """
    A = tmp_path / "A"
    A.mkdir()
    # Root .gitignore
    (A / ".gitignore").write_text("g.txt\n")
    # Subdirectory B with its own .gitignore
    B = A / "B"
    B.mkdir()
    (B / ".gitignore").write_text("b2.txt\n")
    # Subdirectory B1
    B1 = B / "B1"
    B1.mkdir()
    (B1 / "b1.txt").touch()
    (B1 / "b2.txt").touch()
    # Subdirectory C without .gitignore
    C = A / "C"
    C.mkdir()
    (C / "c1.txt").touch()
    (C / "c2.txt").touch()
    # Files in A
    (A / "f.txt").touch()
    (A / "g.txt").touch()
    return A


@pytest.fixture
def setup_multiple_git_repos(tmp_path):
    """
    Sets up a directory structure with multiple git repositories:
    /A
        /Repo1
            .gitignore (ignore 'a1.txt')
            a1.txt
            a2.txt
        /Repo2
            .gitignore (ignore 'b1.txt')
            b1.txt
            b2.txt
        c1.txt
        c2.txt
    """
    A = tmp_path / "A"
    A.mkdir()
    # Repository 1
    Repo1 = A / "Repo1"
    Repo1.mkdir()
    (Repo1 / ".gitignore").write_text("a1.txt\n")
    (Repo1 / "a1.txt").touch()
    (Repo1 / "a2.txt").touch()
    # Repository 2
    Repo2 = A / "Repo2"
    Repo2.mkdir()
    (Repo2 / ".gitignore").write_text("b1.txt\n")
    (Repo2 / "b1.txt").touch()
    (Repo2 / "b2.txt").touch()
    # Files in A
    (A / "c1.txt").touch()
    (A / "c2.txt").touch()
    return A


@pytest.fixture
def setup_specific_ignore_folders(tmp_path):
    """
    Sets up a directory structure with specific folders to ignore:
    /A
        /venv
            v1.txt
        /__pycache__
            p1.txt
        /src
            s1.txt
        main.py
    """
    A = tmp_path / "A"
    A.mkdir()
    # Folders to ignore
    venv = A / "venv"
    venv.mkdir()
    (venv / "v1.txt").touch()

    pycache = A / "__pycache__"
    pycache.mkdir()
    (pycache / "p1.txt").touch()

    # Folder not to ignore
    src = A / "src"
    src.mkdir()
    (src / "s1.txt").touch()

    # File
    (A / "main.py").touch()

    return A


def traverse_to_dict(node: TreeNode) -> dict:
    """
    Helper function to convert TreeNode to dict for easier assertions.
    """
    result = {
        "name": node.name,
        "path": node.get_path(),
        "is_file": node.is_file,
        "children": []
    }
    for child in node.children:
        result["children"].append(traverse_to_dict(child))
    return result


def test_basic_directory_structure(setup_basic_directory, capsys):
    """
    Test that directories are listed before files and both are sorted alphabetically.
    """
    A = setup_basic_directory
    traversal = DirectoryTraversal(
        strategies=[],  # No ignore strategies
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(A))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "B", "path": "A/B", "is_file": False, "children": []},
        {"name": "C", "path": "A/C", "is_file": False, "children": []},
        {"name": "D", "path": "A/D", "is_file": False, "children": []},
        {"name": "f.txt", "path": "A/f.txt", "is_file": True, "children": []},
        {"name": "g.txt", "path": "A/g.txt", "is_file": True, "children": []},
        {"name": "h.txt", "path": "A/h.txt", "is_file": True, "children": []},
    ]

    expected = {
        "name": "A",
        "path": "A",
        "is_file": False,
        "children": expected_children
    }

    # Debugging: Print the actual and expected tree_dict for inspection
    captured = capsys.readouterr()
    print("Actual Tree Structure:", tree_dict)
    print("Expected Tree Structure:", expected)

    assert tree_dict == expected


def test_nested_gitignore(setup_nested_gitignore):
    """
    Test that .gitignore files in nested directories are respected.
    """
    A = setup_nested_gitignore
    # Initialize ignore strategies: Ignore .gitignore files and handle folder ignores
    specific_ignore = SpecificFolderIgnoreStrategy(folders_to_ignore=[])  # No specific folders to ignore in this test
    dot_ignore = DotIgnoreStrategy()
    traversal = DirectoryTraversal(
        strategies=[dot_ignore],  # Use DotIgnoreStrategy to ignore .gitignore files
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(A))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "B", "path": "A/B", "is_file": False, "children": [
            {"name": "B1", "path": "A/B/B1", "is_file": False, "children": [
                {"name": "b1.txt", "path": "A/B/B1/b1.txt", "is_file": True, "children": []},
                # b2.txt is ignored by B's .gitignore
            ]}
        ]},
        {"name": "C", "path": "A/C", "is_file": False, "children": [
            {"name": "c1.txt", "path": "A/C/c1.txt", "is_file": True, "children": []},
            {"name": "c2.txt", "path": "A/C/c2.txt", "is_file": True, "children": []},
        ]},
        {"name": "f.txt", "path": "A/f.txt", "is_file": True, "children": []},
        # g.txt is ignored by root .gitignore
    ]

    expected = {
        "name": "A",
        "path": "A",
        "is_file": False,
        "children": expected_children
    }

    assert tree_dict == expected


def test_multiple_git_repositories(setup_multiple_git_repos):
    """
    Test handling of multiple .gitignore files in different repositories.
    """
    A = setup_multiple_git_repos
    # Initialize ignore strategies: Ignore .gitignore files
    traversal = DirectoryTraversal(
        strategies=[DotIgnoreStrategy()],  # Use DotIgnoreStrategy to ignore .gitignore files
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(A))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "Repo1", "path": "A/Repo1", "is_file": False, "children": [
            {"name": "a2.txt", "path": "A/Repo1/a2.txt", "is_file": True, "children": []},
            # a1.txt is ignored by Repo1's .gitignore
        ]},
        {"name": "Repo2", "path": "A/Repo2", "is_file": False, "children": [
            {"name": "b2.txt", "path": "A/Repo2/b2.txt", "is_file": True, "children": []},
            # b1.txt is ignored by Repo2's .gitignore
        ]},
        {"name": "c1.txt", "path": "A/c1.txt", "is_file": True, "children": []},
        {"name": "c2.txt", "path": "A/c2.txt", "is_file": True, "children": []},
    ]

    expected = {
        "name": "A",
        "path": "A",
        "is_file": False,
        "children": expected_children
    }

    assert tree_dict == expected


def test_specific_folder_ignore(setup_specific_ignore_folders):
    """
    Test that specific folders are ignored based on SpecificFolderIgnoreStrategy.
    """
    A = setup_specific_ignore_folders
    # Initialize ignore strategies
    specific_ignore = SpecificFolderIgnoreStrategy(folders_to_ignore=["venv", "__pycache__"])
    dot_ignore = DotIgnoreStrategy()
    traversal = DirectoryTraversal(
        strategies=[specific_ignore, dot_ignore],
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(A))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "src", "path": "A/src", "is_file": False, "children": [
            {"name": "s1.txt", "path": "A/src/s1.txt", "is_file": True, "children": []},
        ]},
        {"name": "main.py", "path": "A/main.py", "is_file": True, "children": []},
        # venv and __pycache__ are ignored
    ]

    assert tree_dict == {
        "name": "A",
        "path": "A",
        "is_file": False,
        "children": expected_children
    }


def test_empty_directory(tmp_path):
    """
    Test traversal of an empty directory.
    """
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    traversal = DirectoryTraversal(
        strategies=[DotIgnoreStrategy()],  # Use DotIgnoreStrategy to ignore .gitignore files
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(empty_dir))
    tree_dict = traverse_to_dict(tree)

    expected = {
        "name": "empty",
        "path": "empty",
        "is_file": False,
        "children": []
    }

    assert tree_dict == expected


def test_directory_with_only_files(tmp_path):
    """
    Test traversal of a directory containing only files.
    """
    dir_path = tmp_path / "files_only"
    dir_path.mkdir()
    for filename in ["a.txt", "b.txt", "c.txt"]:
        (dir_path / filename).touch()

    traversal = DirectoryTraversal(
        strategies=[DotIgnoreStrategy()],  # Use DotIgnoreStrategy to ignore .gitignore files
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(dir_path))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "a.txt", "path": "files_only/a.txt", "is_file": True, "children": []},
        {"name": "b.txt", "path": "files_only/b.txt", "is_file": True, "children": []},
        {"name": "c.txt", "path": "files_only/c.txt", "is_file": True, "children": []},
    ]

    expected = {
        "name": "files_only",
        "path": "files_only",
        "is_file": False,
        "children": expected_children
    }

    assert tree_dict == expected


def test_directory_with_only_folders(tmp_path):
    """
    Test traversal of a directory containing only folders.
    """
    dir_path = tmp_path / "folders_only"
    dir_path.mkdir()
    for folder in ["A", "B", "C"]:
        (dir_path / folder).mkdir()

    traversal = DirectoryTraversal(
        strategies=[DotIgnoreStrategy()],  # Use DotIgnoreStrategy to ignore .gitignore files
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(dir_path))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "A", "path": "folders_only/A", "is_file": False, "children": []},
        {"name": "B", "path": "folders_only/B", "is_file": False, "children": []},
        {"name": "C", "path": "folders_only/C", "is_file": False, "children": []},
    ]

    expected = {
        "name": "folders_only",
        "path": "folders_only",
        "is_file": False,
        "children": expected_children
    }

    assert tree_dict == expected


def test_case_sensitivity(tmp_path):
    """
    Test that sorting is case-insensitive if implemented so.
    """
    dir_path = tmp_path / "case_test"
    dir_path.mkdir()
    # Create mixed case entries
    entries = ["a_folder", "B_folder", "c_folder", "A_file.txt", "b_file.txt", "C_file.txt"]
    for entry in entries:
        if 'folder' in entry:
            (dir_path / entry).mkdir()
        else:
            (dir_path / entry).touch()

    traversal = DirectoryTraversal(
        strategies=[DotIgnoreStrategy()],  # Use DotIgnoreStrategy to ignore .gitignore files
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(dir_path))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "a_folder", "path": "case_test/a_folder", "is_file": False, "children": []},
        {"name": "B_folder", "path": "case_test/B_folder", "is_file": False, "children": []},
        {"name": "c_folder", "path": "case_test/c_folder", "is_file": False, "children": []},
        {"name": "A_file.txt", "path": "case_test/A_file.txt", "is_file": True, "children": []},
        {"name": "b_file.txt", "path": "case_test/b_file.txt", "is_file": True, "children": []},
        {"name": "C_file.txt", "path": "case_test/C_file.txt", "is_file": True, "children": []},
    ]

    expected = {
        "name": "case_test",
        "path": "case_test",
        "is_file": False,
        "children": expected_children
    }

    assert tree_dict == expected


def test_permission_error(tmp_path, monkeypatch):
    """
    Test that traversal handles directories with permission errors gracefully.
    """
    A = tmp_path / "A"
    A.mkdir()
    B = A / "B"
    B.mkdir()
    (A / "file1.txt").touch()
    (B / "file2.txt").touch()

    # Mock os.listdir to raise PermissionError for directory B
    def mock_listdir(path):
        if path == str(B):
            raise PermissionError("Permission denied")
        return os.listdir_original(path)

    # Backup the original os.listdir
    os.listdir_original = os.listdir
    monkeypatch.setattr(os, "listdir", mock_listdir)

    traversal = DirectoryTraversal(
        strategies=[DotIgnoreStrategy()],  # Use DotIgnoreStrategy to ignore .gitignore files
        sort_strategy=DefaultSortStrategy()
    )
    tree = traversal.build_tree(str(A))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "B", "path": "A/B", "is_file": False, "children": []},  # B's children are not listed due to PermissionError
        {"name": "file1.txt", "path": "A/file1.txt", "is_file": True, "children": []},
    ]

    assert tree_dict == {
        "name": "A",
        "path": "A",
        "is_file": False,
        "children": expected_children
    }


def test_dot_ignore_strategy(tmp_path):
    """
    Test that DotIgnoreStrategy correctly ignores hidden files and folders.
    """
    A = tmp_path / "A"
    A.mkdir()
    # Create hidden files and folders
    hidden_folder = A / ".hidden_folder"
    hidden_folder.mkdir()
    (hidden_folder / "hidden_file.txt").touch()
    (A / ".hidden_file.txt").touch()
    # Create visible files and folders
    visible_folder = A / "visible_folder"
    visible_folder.mkdir()
    (visible_folder / "visible_file.txt").touch()
    (A / "visible_file.txt").touch()

    # Initialize ignore strategies
    dot_ignore = DotIgnoreStrategy()
    traversal = DirectoryTraversal(
        strategies=[dot_ignore],
        sort_strategy=DefaultSortStrategy()
    )

    tree = traversal.build_tree(str(A))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "visible_folder", "path": "A/visible_folder", "is_file": False, "children": [
            {"name": "visible_file.txt", "path": "A/visible_folder/visible_file.txt", "is_file": True, "children": []},
        ]},
        {"name": "visible_file.txt", "path": "A/visible_file.txt", "is_file": True, "children": []},
        # Hidden files and folders are ignored
    ]

    assert tree_dict == {
        "name": "A",
        "path": "A",
        "is_file": False,
        "children": expected_children
    }


def test_specific_and_gitignore_combined(tmp_path):
    """
    Test combining SpecificFolderIgnoreStrategy with .gitignore files.
    """
    A = tmp_path / "A"
    A.mkdir()
    # Create folders
    ignored_folder = A / "ignored_folder"
    ignored_folder.mkdir()
    (ignored_folder / "file1.txt").touch()

    repo_folder = A / "repo"
    repo_folder.mkdir()
    (repo_folder / ".gitignore").write_text("repo_file2.txt\n")
    (repo_folder / "repo_file1.txt").touch()
    (repo_folder / "repo_file2.txt").touch()

    # Create non-ignored files
    (A / "file3.txt").touch()

    # Initialize ignore strategies
    specific_ignore = SpecificFolderIgnoreStrategy(folders_to_ignore=["ignored_folder"])
    dot_ignore = DotIgnoreStrategy()  # To ignore .gitignore files
    traversal = DirectoryTraversal(
        strategies=[specific_ignore, dot_ignore],
        sort_strategy=DefaultSortStrategy()
    )

    tree = traversal.build_tree(str(A))
    tree_dict = traverse_to_dict(tree)

    expected_children = [
        {"name": "repo", "path": "A/repo", "is_file": False, "children": [
            {"name": "repo_file1.txt", "path": "A/repo/repo_file1.txt", "is_file": True, "children": []},
            # repo_file2.txt is ignored by .gitignore
        ]},
        {"name": "file3.txt", "path": "A/file3.txt", "is_file": True, "children": []},
        # ignored_folder is ignored
    ]

    assert tree_dict == expected_children
