# File: autobyteus_server/api/graphql/queries/file_explorer_queries.py

"""
Module: file_explorer_queries

This module provides GraphQL queries related to file explorer operations.
"""

import json
import logging
import strawberry
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

# Singleton instance
workspace_manager = WorkspaceManager()

logger = logging.getLogger(__name__)

@strawberry.type
class Query:
    @strawberry.field
    def file_content(self, workspace_id: str, file_path: str) -> str:
        """
        Fetches the content of a file using its relative path from the workspace root.

        Args:
            workspace_id (str): The ID of the workspace.
            file_path (str): The relative path of the file from the workspace root.

        Returns:
            str: The content of the file.
        """
        try:
            workspace = workspace_manager.get_workspace_by_id(workspace_id)
            if not workspace:
                return json.dumps({"error": "Workspace not found"})

            file_explorer = workspace.get_file_explorer()
            return file_explorer.read_file_content(file_path)
        except FileNotFoundError as e:
            return json.dumps({"error": f"File not found: {str(e)}"})
        except PermissionError as e:
            return json.dumps({"error": f"Permission denied: {str(e)}"})
        except ValueError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
            return json.dumps({"error": "An unexpected error occurred while reading the file"})
