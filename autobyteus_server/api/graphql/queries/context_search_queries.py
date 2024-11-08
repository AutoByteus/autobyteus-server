"""
Module: context_search_queries

This module provides GraphQL queries related to context-specific search operations,
particularly focused on hackathon workspace searches.
"""

import logging
from typing import List
import strawberry
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

workspace_manager = WorkspaceManager()
logger = logging.getLogger(__name__)

@strawberry.type
class ContextQuery:
    @strawberry.field
    def hackathon_search(self, workspace_id: str, query: str) -> List[str]:
        """
        Performs a hackathon-specific search within the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace to search in.
            query (str): The search query.

        Returns:
            List[str]: A list of file paths that match the search query.
        """
        try:
            workspace = workspace_manager.get_workspace_by_id(workspace_id)
            if not workspace:
                logger.error(f"Workspace not found: {workspace_id}")
                return []

            search_result = workspace.hackathon_search_service.search(query)
            return search_result.paths
        except Exception as e:
            error_message = f"Error during hackathon search: {str(e)}"
            logger.error(error_message)
            return []