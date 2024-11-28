from abc import ABC, abstractmethod
from autobyteus_server.codeverse.core.code_entities.module_entity import ModuleEntity

class BaseCodeParser(ABC):
    @abstractmethod
    def parse_source_code(self, filepath: str) -> ModuleEntity:
        pass