"""
Represents a workspace containing project configurations, file exploration, and automated workflows.

This class stores the parsed workspace structure along with associated objects such as
file explorer and automated coding workflows. It manages the project type and provides
access to the directory tree and workflow functionalities.
"""

import uuid
from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.workspaces.setting.project_types import ProjectType
from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow
from autobyteus_server.workspaces.workspace_tools.command_executor import CommandExecutionResult, CommandExecutor


class Workspace:
    """
    Represents a workspace containing project configurations, file exploration, and automated workflows.

    This class stores the parsed workspace structure along with associated objects such as
    file explorer and automated coding workflows. It manages the project type and provides
    access to the directory tree and workflow functionalities.
    """

    def __init__(
        self,
        root_path: str,
        project_type: ProjectType,
        file_explorer: FileExplorer = None,
        workflow: AutomatedCodingWorkflow = None
    ):
        """
        Initialize a Workspace instance.

        Args:
            root_path (str): The root directory path of the workspace.
            project_type (ProjectType): The type of the project, defined by the ProjectType enum.
            file_explorer (FileExplorer, optional): An instance of FileExplorer to navigate the workspace files.
                Defaults to None.
            workflow (AutomatedCodingWorkflow, optional): An instance of AutomatedCodingWorkflow to handle
                automated coding tasks within the workspace. Defaults to None.
        """
        self.root_path = root_path
        self.project_type = project_type
        self.name = root_path  # Name is set to root_path
        self.workspace_id = str(uuid.uuid4())
        self.file_explorer: FileExplorer = file_explorer
        self._workflow: AutomatedCodingWorkflow = workflow
        self._command_executor: CommandExecutor = None

    @property
    def project_type(self) -> ProjectType:
        """
        Get the type of the project.

        Returns:
            ProjectType: The current project type as defined by the ProjectType enum.
        """
        return self._project_type

    @project_type.setter
    def project_type(self, value: ProjectType):
        """
        Set the type of the project.

        Args:
            value (ProjectType): The new project type, defined by the ProjectType enum.

        Raises:
            ValueError: If the provided value is not an instance of ProjectType.
        """
        if not isinstance(value, ProjectType):
            raise ValueError("project_type must be an instance of the ProjectType enum.")
        self._project_type = value

    def get_file_explorer(self) -> FileExplorer:
        """
        Retrieve the FileExplorer instance for navigating the workspace's directory structure.

        If the FileExplorer is not already initialized, it will be created using the workspace's root path.

        Returns:
            FileExplorer: The FileExplorer instance associated with this workspace.
        """
        if self.file_explorer is None:
            self.file_explorer = FileExplorer(self.root_path)
        return self.file_explorer

    def set_file_explorer(self, file_explorer: FileExplorer):
        """
        Assign a FileExplorer instance to manage the workspace's directory tree.

        Args:
            file_explorer (FileExplorer): The FileExplorer instance to be associated with this workspace.
        """
        self.file_explorer = file_explorer

    @property
    def workflow(self) -> AutomatedCodingWorkflow:
        """
        Get the automated coding workflow associated with this workspace.

        Returns:
            AutomatedCodingWorkflow: The workflow handling automated coding tasks.
        """
        return self._workflow

    @workflow.setter
    def workflow(self, value: AutomatedCodingWorkflow):
        """
        Assign an automated coding workflow to the workspace.

        Args:
            value (AutomatedCodingWorkflow): The AutomatedCodingWorkflow instance to associate with this workspace.

        Raises:
            ValueError: If the provided value is not an instance of AutomatedCodingWorkflow.
        """
        if not isinstance(value, AutomatedCodingWorkflow):
            raise ValueError("workflow must be an instance of AutomatedCodingWorkflow.")
        self._workflow = value

    def get_command_executor(self) -> CommandExecutor:
        """
        Get the CommandExecutor instance for this workspace.

        Returns:
            CommandExecutor: The command executor for this workspace.
        """
        if self._command_executor is None:
            self._command_executor = CommandExecutor(self.root_path)
        return self._command_executor

    def execute_command(self, command: str) -> CommandExecutionResult:
        """
        Execute a command in this workspace.

        Args:
            command (str): The command to execute.

        Returns:
            CommandExecutionResult: The result of the command execution.
        """
        executor = self.get_command_executor()
        return executor.execute_command(command)