"""
Module: workspace_queries

This module provides GraphQL queries related to workspace operations.
"""

import json
import logging
from typing import List

import strawberry
from strawberry.scalars import JSON

from autobyteus_server.api.graphql.types.workspace_info import WorkspaceInfo
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.workspaces.workspace_tools_service import (
    WorkspaceToolsService
)

# Singleton instances
workspace_manager = WorkspaceManager()
workspace_tools_service = WorkspaceToolsService()

logger = logging.getLogger(__name__)


@strawberry.type
class WorkspaceTool:
    name: str
    prompt_template: str



@strawberry.type
class Query:
    @strawberry.field
    def workflow_config(self, workspace_id: str) -> JSON:
        """
        Fetches the configuration for the workflow associated with the
        provided workspace.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            JSON: The configuration of the workflow.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            return json.dumps({"error": "Workspace not found"})

        workflow = workspace.workflow
        if not workflow:
            return json.dumps(
                {"error": "Workflow not initialized for this workspace"}
            )

        return workflow.to_json()

    @strawberry.field
    def get_available_workspace_tools(
        self, workspace_id: str
    ) -> List['WorkspaceTool']:
        """
        Fetches available workspace tools for the given workspace.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            List[WorkspaceTool]: A list of available workspace tools.

        Raises:
            Exception: If fetching available workspace tools fails.
        """
        try:
            workspace = workspace_manager.get_workspace_by_id(workspace_id)
            if not workspace:
                raise Exception(f"Workspace not found for ID: {workspace_id}")
            
            tools_data = workspace_tools_service.get_available_tools(
                workspace.root_path
            )
            return [
                WorkspaceTool(
                    name=tool_data.name, prompt_template=tool_data.prompt_template
                )
                for tool_data in tools_data
            ]
        except Exception as e:
            raise Exception(
                f"Failed to fetch available workspace tools: {str(e)}"
            )

    @strawberry.field
    def all_workspaces(self) -> List[WorkspaceInfo]:
        """
        Retrieves all workspaces.

        Returns:
            List[WorkspaceInfo]: A list of all workspace information objects.
        """
        try:
            workspaces = workspace_manager.get_all_workspaces()
            logger.info(f"Retrieved {len(workspaces)} workspaces.")
            return [
                WorkspaceInfo(
                    workspace_id=ws.workspace_id,
                    name=ws.name,
                    file_explorer=ws.file_explorer.to_json()
                ) for ws in workspaces
            ]
        except Exception as e:
            logger.error(f"Failed to retrieve all workspaces: {str(e)}")
            raise Exception("Unable to fetch workspaces at this time.")