from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Request
from fastapi.responses import JSONResponse
import os
import uuid
import logging
from typing import List
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

router = APIRouter()

# Initialize logger
logger = logging.getLogger(__name__)

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
    request: Request,
    file: UploadFile = File(...),
    workspace_id: str = Form(...)
):
    # Validate workspace
    workspace = workspace_manager.get_workspace_by_id(workspace_id)
    if not workspace:
        logger.error(f"Invalid workspace ID: {workspace_id}")
        raise HTTPException(status_code=400, detail=f"Invalid workspace ID: {workspace_id}")

    # Define base upload directory based on workspace root path
    workspace_root_path = workspace.root_path
    BASE_UPLOAD_DIRECTORY = os.path.join(workspace_root_path, "uploads")

    if not os.path.exists(BASE_UPLOAD_DIRECTORY):
        try:
            os.makedirs(BASE_UPLOAD_DIRECTORY, exist_ok=True)
            logger.info(f"Created base upload directory: {BASE_UPLOAD_DIRECTORY}")
        except Exception as e:
            logger.exception("Failed to create upload directory.")
            raise HTTPException(status_code=500, detail=f"Failed to create upload directory: {str(e)}")

    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.error(f"Unsupported file type: {file.content_type}")
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
                logger.error("File size exceeds the limit of 10MB.")
                raise HTTPException(status_code=400, detail="File size exceeds the limit of 10MB.")
    except Exception as e:
        logger.exception("Error reading file.")
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    # Check workspace storage quota
    total_size = 0
    for root, dirs, files in os.walk(BASE_UPLOAD_DIRECTORY):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
            except Exception as e:
                logger.warning(f"Could not get size for file {fp}: {str(e)}")
    if total_size + len(content) > MAX_WORKSPACE_STORAGE:
        logger.error("Workspace storage quota exceeded.")
        raise HTTPException(status_code=400, detail="Workspace storage quota exceeded.")

    # Determine file category
    category = get_category(file.content_type)

    # Create category directory if it doesn't exist
    category_directory = os.path.join(BASE_UPLOAD_DIRECTORY, category)
    if not os.path.exists(category_directory):
        try:
            os.makedirs(category_directory, exist_ok=True)
            logger.info(f"Created category directory: {category_directory}")
        except Exception as e:
            logger.exception("Failed to create category directory.")
            raise HTTPException(status_code=500, detail=f"Failed to create category directory: {str(e)}")

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(category_directory, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        logger.info(f"File saved successfully: {file_path}")
    except Exception as e:
        logger.exception("Failed to save file.")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Construct URL for accessing the uploaded file using the new files endpoint
    # The URL pattern is now: {base_url}rest/files/{workspace_id}/{category}/{unique_filename}
    base_url = str(request.base_url)
    file_url = f"{base_url}rest/files/{workspace_id}/{category}/{unique_filename}"
    logger.info(f"Returning file URL: {file_url}")
    return JSONResponse(content={"fileUrl": file_url})
