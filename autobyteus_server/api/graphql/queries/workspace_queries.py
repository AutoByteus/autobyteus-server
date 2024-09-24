"""
Module: workspace_queries

This module provides GraphQL queries related to workspace operations.
"""

import json
import logging
from typing import List
import strawberry
from strawberry.scalars import JSON
from autobyteus_server.codeverse.search.search_service import SearchService
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.workspaces.workspace_tools_service import WorkspaceToolsService

# Singleton instances
workspace_manager = WorkspaceManager()
workspace_tools_service = WorkspaceToolsService()
search_service = SearchService()  # Instantiate SearchService

logger = logging.getLogger(__name__)

@strawberry.type
class WorkspaceTool:
    name: str
    prompt_template: str

@strawberry.type
class Query:
    @strawberry.field
    def workflow_config(self, workspace_root_path: str) -> JSON:
        """
        Fetches the configuration for the workflow associated with the provided workspace.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            JSON: The configuration of the workflow.
        """
        workspace = workspace_manager.get_workspace(workspace_root_path)
        if not workspace:
            return json.dumps({"error": "Workspace not found"})

        workflow = workspace.workflow
        if not workflow:
            return json.dumps({"error": "Workflow not initialized for this workspace"})

        return workflow.to_json()

    @strawberry.field
    def get_available_workspace_tools(self, workspace_root_path: str) -> List[WorkspaceTool]:
        try:
            tools_data = workspace_tools_service.get_available_tools(workspace_root_path)
            return [WorkspaceTool(name=tool_data.name, prompt_template=tool_data.prompt_template) for tool_data in tools_data]
        except Exception as e:
            raise Exception(f"Failed to fetch available workspace tools: {str(e)}")