import logging
from typing import Optional, List

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus.utils.singleton import SingletonMeta
from autobyteus_server.workspaces.workspace import Workspace
from autobyteus_server.workspaces.workspace_registry import WorkspaceRegistry
from autobyteus_server.workspaces.workspace_tools.project_type_determiner import ProjectTypeDeterminer

from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow

logger = logging.getLogger(__name__)

class WorkspaceManager(metaclass=SingletonMeta):
    """
    Manager to handle operations related to workspaces.

    Attributes:
        workspace_registry (WorkspaceRegistry): A registry to store workspaces.
        project_type_determiner (ProjectTypeDeterminer): A tool to determine the project type.
    """

    def __init__(self):
        """
        Initialize WorkspaceManager.
        """
        self.workspace_registry = WorkspaceRegistry()
        self.project_type_determiner = ProjectTypeDeterminer()

    def get_workspace_file_explorer(self, workspace_id: str) -> Optional[FileExplorer]:
        """
        Retrieves the FileExplorer for a given workspace ID if it exists.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            Optional[FileExplorer]: The FileExplorer object if the workspace exists, None otherwise.
        """
        workspace = self.workspace_registry.get_workspace_by_id(workspace_id)
        return workspace.file_explorer if workspace else None

    def add_workspace(self, workspace_root_path: str) -> Workspace:
        """
        Adds a workspace to the workspace registry or returns the existing one.
        If the workspace doesn't exist, it builds the directory tree of the workspace
        and initializes an AutomatedCodingWorkflow for the workspace.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            Workspace: The created or existing Workspace object.
        """
        existing_workspace = self.workspace_registry.get_workspace_by_root_path(workspace_root_path)
        if existing_workspace:
            logger.info(f"Workspace already exists at path: {workspace_root_path}")
            return existing_workspace

        # Determine the project type
        project_type = self.project_type_determiner.determine(workspace_root_path)
        logger.info(f"Determined project type '{project_type}' for workspace at {workspace_root_path}")

        # Build the directory tree
        file_explorer = FileExplorer(workspace_root_path)
        file_explorer.build_workspace_directory_tree()
        logger.info(f"Built directory tree for workspace at {workspace_root_path}")

        # Create the workflow
        workflow = AutomatedCodingWorkflow()
        logger.info(f"Initialized AutomatedCodingWorkflow for workspace at {workspace_root_path}")

        # Create and register the Workspace
        workspace = Workspace(root_path=workspace_root_path, 
                              project_type=project_type, file_explorer=file_explorer, workflow=workflow)
        
        workflow.workspace = workspace
        
        self.workspace_registry.add_workspace(workspace)
        logger.info(f"Workspace with ID {workspace.workspace_id} added to registry.")

        return workspace

    def get_workspace_by_root_path(self, workspace_root_path: str) -> Optional[Workspace]:
        """
        Retrieves a workspace from the workspace registry using the root path.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            Optional[Workspace]: The workspace if it exists, None otherwise.
        """
        return self.workspace_registry.get_workspace_by_root_path(workspace_root_path)

    def get_workspace_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """
        Retrieves a workspace using its ID.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            Optional[Workspace]: The workspace if it exists, None otherwise.
        """
        return self.workspace_registry.get_workspace_by_id(workspace_id)

    def get_all_workspaces(self) -> List[Workspace]:
        """
        Retrieves all registered workspaces.

        Returns:
            List[Workspace]: A list of all Workspace objects.
        """
        return self.workspace_registry.get_all_workspaces()