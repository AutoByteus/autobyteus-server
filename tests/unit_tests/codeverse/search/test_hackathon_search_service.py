import pytest
from autobyteus_server.codeverse.search.hackathon_search_service import HackathonSearchService
from autobyteus_server.codeverse.search.search_result import SearchResult
from typing import List


@pytest.fixture
def search_service() -> HackathonSearchService:
    """
    Fixture that provides a HackathonSearchService instance.
    """
    return HackathonSearchService()


@pytest.fixture
def expected_paths() -> List[str]:
    """
    Fixture that provides the expected paths for all tests.
    """
    return [
        "src/project/module1/file1.py",
        "src/project/module2/file2.py",
        "src/project/module3/file3.py"
    ]


def test_search_returns_fixed_paths(search_service: HackathonSearchService, expected_paths: List[str]) -> None:
    """
    Test that search returns the expected fixed paths for a regular query.
    """
    result: SearchResult = search_service.search("any query")
    assert result.paths == expected_paths


def test_search_with_empty_query(search_service: HackathonSearchService, expected_paths: List[str]) -> None:
    """
    Test that search handles empty query strings correctly.
    """
    result: SearchResult = search_service.search("")
    assert result.paths == expected_paths


def test_search_with_special_characters(search_service: HackathonSearchService, expected_paths: List[str]) -> None:
    """
    Test that search handles queries containing special characters correctly.
    """
    result: SearchResult = search_service.search("!@#$%^&*()")
    assert result.paths == expected_paths