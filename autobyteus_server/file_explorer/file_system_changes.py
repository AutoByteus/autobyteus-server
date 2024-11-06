from enum import Enum
from typing import List, Union, Optional, Literal, Any, Dict
from dataclasses import dataclass, field
import json

from autobyteus_server.file_explorer.tree_node import TreeNode  # Ensure TreeNode is available


class ChangeType(str, Enum):
    ADD = "add"
    DELETE = "delete"
    RENAME = "rename"


@dataclass
class FileSystemChange:
    type: ChangeType

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FileSystemChange':
        change_type = ChangeType(data["type"])
        if change_type == ChangeType.ADD:
            return AddChange.from_dict(data)
        elif change_type == ChangeType.DELETE:
            return DeleteChange.from_dict(data)
        elif change_type == ChangeType.RENAME:
            return RenameChange.from_dict(data)
        else:
            raise ValueError(f"Unknown ChangeType: {change_type}")


@dataclass
class AddChange(FileSystemChange):
    type: Literal[ChangeType.ADD] = ChangeType.ADD
    node: TreeNode = field(default_factory=TreeNode)
    parent_id: str = ""

    def _node_to_dict(self, node: TreeNode) -> Dict[str, Any]:
        """
        Custom node serialization that excludes children information.
        """
        return {
            "name": node.name,
            "path": node.get_path(),
            "is_file": node.is_file,
            "id": node.id,
            "children": []  # Always empty array to maintain structure without children
        }

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "node": self._node_to_dict(self.node),
            "parent_id": self.parent_id,
        })
        return base

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AddChange':
        node = TreeNode.from_dict(data["node"])
        parent_id = data["parent_id"]
        return AddChange(node=node, parent_id=parent_id)


@dataclass
class DeleteChange(FileSystemChange):
    type: Literal[ChangeType.DELETE] = ChangeType.DELETE
    node_id: str = ""
    parent_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "node_id": self.node_id,
            "parent_id": self.parent_id,
        })
        return base

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeleteChange':
        node_id = data["node_id"]
        parent_id = data["parent_id"]
        return DeleteChange(node_id=node_id, parent_id=parent_id)


@dataclass
class RenameChange(FileSystemChange):
    type: Literal[ChangeType.RENAME] = ChangeType.RENAME
    node: TreeNode = field(default_factory=TreeNode)
    parent_id: str = ""
    previous_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "node": self.node.to_dict(),
            "parent_id": self.parent_id,
            "previous_id": self.previous_id,
        })
        return base

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RenameChange':
        node = TreeNode.from_dict(data["node"])
        parent_id = data["parent_id"]
        previous_id = data.get("previous_id")
        return RenameChange(node=node, parent_id=parent_id, previous_id=previous_id)


@dataclass
class FileSystemChangeEvent:
    changes: List[FileSystemChange] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "changes": [change.to_dict() for change in self.changes]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FileSystemChangeEvent':
        changes = [FileSystemChange.from_dict(change_data) for change_data in data["changes"]]
        return FileSystemChangeEvent(changes=changes)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_data: str) -> 'FileSystemChangeEvent':
        data = json.loads(json_data)
        return FileSystemChangeEvent.from_dict(data)


def serialize_change_event(event: FileSystemChangeEvent) -> str:
    return event.to_json()


def deserialize_change_event(json_data: str) -> FileSystemChangeEvent:
    return FileSystemChangeEvent.from_json(json_data)