from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import logging
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

router = APIRouter(prefix="/files", tags=["files"])

# Initialize logger
logger = logging.getLogger(__name__)

workspace_manager = WorkspaceManager()

@router.get("/{workspace_id}/{category}/{filename}")
async def get_file(workspace_id: str, category: str, filename: str):
    # Validate workspace
    workspace = workspace_manager.get_workspace_by_id(workspace_id)
    if not workspace:
        logger.error(f"Invalid workspace ID: {workspace_id}")
        raise HTTPException(status_code=400, detail="Invalid workspace ID.")

    file_path = os.path.join(workspace.root_path, "uploads", category, filename)
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found.")

    logger.info(f"Serving file: {file_path}")
    return FileResponse(file_path)
