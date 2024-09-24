# autobyteus_server/workspaces/setting/workspace.py

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.workspaces.setting.project_types import ProjectType
from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow


class Workspace:
    """
    Class to store the parsed workspace structure and other related objects.
    """

    def __init__(self, root_path: str, project_type: ProjectType, file_explorer: FileExplorer = None, workflow: AutomatedCodingWorkflow = None):
        """
        Initialize a Workspace.

        Args:
            root_path (str): The root path of the workspace.
            project_type (ProjectType): The type of the project defined by the ProjectType enum.
            file_explorer (FileExplorer, optional): The file explorer of the workspace. Defaults to None.
            workflow (AutomatedCodingWorkflow, optional): The automated coding workflow for this workspace. Defaults to None.
        """
        self.root_path = root_path
        self.project_type = project_type
        self.directory_tree: FileExplorer = file_explorer
        self._workflow: AutomatedCodingWorkflow = workflow

    @property
    def project_type(self) -> ProjectType:
        """
        Get the type of the project.

        Returns:
            ProjectType: The type of the project as defined by the ProjectType enum.
        """
        return self._project_type

    @project_type.setter
    def project_type(self, value: ProjectType):
        """
        Set the type of the project.

        Args:
            value (ProjectType): The type of the project as defined by the ProjectType enum.
        """
        if not isinstance(value, ProjectType):
            raise ValueError("project_type must be an instance of the ProjectType enum.")
        self._project_type = value

    def set_directory_tree(self, directory_tree: FileExplorer):
        """
        Set the directory tree of the workspace.

        Args:
            directory_tree (FileExplorer): The file explorer of the workspace.
        """
        self.directory_tree = directory_tree

    @property
    def workflow(self) -> AutomatedCodingWorkflow:
        """
        Get the automated coding workflow for this workspace.

        Returns:
            AutomatedCodingWorkflow: The workflow associated with this workspace.
        """
        return self._workflow

    @workflow.setter
    def workflow(self, value: AutomatedCodingWorkflow):
        """
        Set the automated coding workflow for this workspace.

        Args:
            value (AutomatedCodingWorkflow): The workflow to associate with this workspace.
        """
        if not isinstance(value, AutomatedCodingWorkflow):
            raise ValueError("workflow must be an instance of AutomatedCodingWorkflow.")
        self._workflow = value