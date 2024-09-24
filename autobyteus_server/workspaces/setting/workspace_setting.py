# autobyteus_server/workspaces/setting/workspace_setting.py



from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.workspaces.setting.project_types import ProjectType


class WorkspaceSetting:
    """
    Class to store the parsed workspace structure and other related objects.
    """

    def __init__(self, root_path: str, project_type: ProjectType, file_explorer: FileExplorer = None):
        """
        Initialize a WorkspaceSetting.

        Args:
            root_path (str): The root path of the workspace.
            project_type (ProjectType): The type of the project defined by the ProjectType enum.
            directory_tree (WorkspaceDirectoryTree, optional): The directory tree of the workspace. Defaults to None.
        """
        self.root_path = root_path
        self.project_type = project_type
        self.directory_tree: FileExplorer = file_explorer

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
            directory_tree (WorkspaceDirectoryTree): The directory tree of the workspace.
        """
        self.directory_tree = directory_tree
