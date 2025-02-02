import os
import pytest
from urllib.parse import urlparse
from fastapi.testclient import TestClient
from autobyteus_server.app import app

# Define a dummy workspace class to simulate a valid workspace.
class DummyWorkspace:
    def __init__(self, root_path: str):
        self.root_path = root_path

# Fixture to create a TestClient for the FastAPI app.
@pytest.fixture
def client():
    return TestClient(app)

# Fixture to provide a dummy workspace using pytest's tmp_path fixture.
@pytest.fixture
def dummy_workspace(tmp_path):
    # tmp_path is a pathlib.Path object; convert to string for compatibility.
    return DummyWorkspace(str(tmp_path))

# Automatically apply this fixture to all tests in this module.
# It monkeypatches the get_workspace_by_id method in both upload_file and files modules to return our dummy workspace when the id is "test_workspace".
@pytest.fixture(autouse=True)
def setup_workspace(dummy_workspace, monkeypatch):
    # Patch the workspace_manager in the upload_file module
    from autobyteus_server.api.rest.upload_file import workspace_manager as upload_workspace_manager
    monkeypatch.setattr(
        upload_workspace_manager,
        "get_workspace_by_id",
        lambda ws_id: dummy_workspace if ws_id == "test_workspace" else None
    )
    # Patch the workspace_manager in the files module
    from autobyteus_server.api.rest.files import workspace_manager as files_workspace_manager
    monkeypatch.setattr(
        files_workspace_manager,
        "get_workspace_by_id",
        lambda ws_id: dummy_workspace if ws_id == "test_workspace" else None
    )

def test_upload_success(client):
    """
    Test that a valid file upload returns a 200 status code with a file URL,
    and that the uploaded file can be retrieved successfully.
    """
    files = {
        "file": ("test.txt", b"Hello, world", "text/plain")
    }
    data = {
        "workspace_id": "test_workspace"
    }
    response = client.post("/rest/upload-file", files=files, data=data)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    assert "fileUrl" in json_data, "Response JSON does not contain 'fileUrl'"
    file_url = json_data["fileUrl"]

    # Extract the path component from the absolute URL.
    path = urlparse(file_url).path
    get_response = client.get(path)
    assert get_response.status_code == 200, f"Failed to retrieve uploaded file from {path}"
    assert get_response.content == b"Hello, world", "Retrieved file content does not match uploaded content"

def test_upload_invalid_workspace(client):
    """
    Test that providing an invalid workspace ID returns a 400 error.
    """
    files = {
        "file": ("test.txt", b"Hello, world", "text/plain")
    }
    data = {
        "workspace_id": "invalid_workspace"
    }
    response = client.post("/rest/upload-file", files=files, data=data)
    assert response.status_code == 400, f"Expected 400 error for invalid workspace, got {response.status_code}"
    json_data = response.json()
    assert "Invalid workspace ID" in json_data["detail"], "Error detail does not mention invalid workspace ID"

def test_upload_unsupported_file_type(client):
    """
    Test that uploading a file with an unsupported MIME type returns a 400 error.
    """
    files = {
        "file": ("test.zip", b"PK\x03\x04", "application/zip")
    }
    data = {
        "workspace_id": "test_workspace"
    }
    response = client.post("/rest/upload-file", files=files, data=data)
    assert response.status_code == 400, f"Expected 400 error for unsupported file type, got {response.status_code}"
    json_data = response.json()
    assert "Unsupported file type" in json_data["detail"], "Error detail does not mention unsupported file type"

def test_upload_file_too_large(client, monkeypatch):
    """
    Test that uploading a file exceeding the maximum allowed size returns a 400 error.
    This test patches MAX_FILE_SIZE to a small value to simulate a large file.
    """
    # Patch MAX_FILE_SIZE in the upload_file module to 100 bytes.
    monkeypatch.setattr("autobyteus_server.api.rest.upload_file.MAX_FILE_SIZE", 100)
    files = {
        "file": ("large.txt", b"a" * 101, "text/plain")
    }
    data = {
        "workspace_id": "test_workspace"
    }
    response = client.post("/rest/upload-file", files=files, data=data)
    assert response.status_code == 400, f"Expected 400 error for oversized file, got {response.status_code}"
    json_data = response.json()
    assert "File size exceeds the limit" in json_data["detail"], "Error detail does not mention file size limit"
