import strawberry
from strawberry.scalars import JSON

@strawberry.type
class WorkspaceInfo:
    workspace_id: str
    name: str  # The name of the workspace, set to root_path
    file_explorer: JSON  # This will be a JSON representation of the file explorer