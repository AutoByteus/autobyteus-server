# File: autobyteus_server/api/rest/upload_file.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
import os
import uuid
from typing import List
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

router = APIRouter()

workspace_manager = WorkspaceManager()

ALLOWED_MIME_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/pdf",
    "text/plain",
    "application/json",
    "text/markdown",
    "video/mp4",
    # Add more as necessary
]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_WORKSPACE_STORAGE = 500 * 1024 * 1024  # 500 MB per workspace

def get_category(mime_type: str) -> str:
    if mime_type.startswith('image/'):
        return 'images'
    elif mime_type.startswith('video/'):
        return 'videos'
    elif mime_type in ['application/pdf', 'application/json']:
        return 'documents'
    elif mime_type.startswith('text/'):
        return 'texts'
    else:
        return 'others'

@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    workspaceRootPath: str = Form(...)
):
    # Validate workspace
    workspace = workspace_manager.get_workspace(workspaceRootPath)
    if not workspace:
        raise HTTPException(status_code=400, detail="Invalid workspace root path.")

    # Define base upload directory based on workspace root path
    BASE_UPLOAD_DIRECTORY = os.path.join(workspaceRootPath, "uploads")

    if not os.path.exists(BASE_UPLOAD_DIRECTORY):
        try:
            os.makedirs(BASE_UPLOAD_DIRECTORY, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create upload directory: {str(e)}")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # Read file content in chunks to enforce size limit
    try:
        content = b''
        while True:
            chunk = await file.read(8192)  # Read in 8KB chunks
            if not chunk:
                break
            content += chunk
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File size exceeds the limit of 10MB.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    # Check workspace storage quota
    total_size = 0
    for root, dirs, files in os.walk(BASE_UPLOAD_DIRECTORY):
        for f in files:
            fp = os.path.join(root, f)
            total_size += os.path.getsize(fp)
    
    if total_size + len(content) > MAX_WORKSPACE_STORAGE:
        raise HTTPException(status_code=400, detail="Workspace storage quota exceeded.")

    # Determine file category
    category = get_category(file.content_type)

    # Create category directory if it doesn't exist
    category_directory = os.path.join(BASE_UPLOAD_DIRECTORY, category)
    if not os.path.exists(category_directory):
        try:
            os.makedirs(category_directory, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create category directory: {str(e)}")

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(category_directory, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Return the absolute file path
    absolute_file_path = os.path.abspath(file_path)
    return JSONResponse(content={"filePath": absolute_file_path})