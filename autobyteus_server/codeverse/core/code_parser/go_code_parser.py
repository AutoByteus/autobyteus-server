from autobyteus_server.codeverse.core.code_parser.base_code_parser import BaseCodeParser
from autobyteus_server.codeverse.core.code_entities.module_entity import ModuleEntity
from autobyteus_server.codeverse.core.code_entities.function_entity import FunctionEntity
from autobyteus_server.codeverse.core.code_entities.class_entity import ClassEntity
from autobyteus_server.file_explorer.file_reader import FileReader
from tree_sitter import Language, Parser
import os

# Ensure the language library is built
LANGUAGE_BUILD_PATH = 'autobyteus-server/autobyteus_server/codeverse/core/code_parser/build/my-languages.so'
if not os.path.exists(LANGUAGE_BUILD_PATH):
    Language.build_library(
        LANGUAGE_BUILD_PATH,
        [
            'tree-sitter-go',
        ]
    )

GO_LANGUAGE = Language(LANGUAGE_BUILD_PATH, 'go')

class GoCodeParser(BaseCodeParser):
    """
    This class provides functionality to parse Go source code.
    """

    def parse_source_code(self, filepath: str) -> ModuleEntity:
        """
        Reads and parses the source code from a .go file and extracts its functions and types.

        Args:
            filepath (str): Path to a .go file.

        Returns:
            A ModuleEntity object containing the file's functions and types,
            or None if the source_code could not be read or parsed.
        """
        source_code = FileReader.read_file(filepath)
        if source_code is None:
            return None

        parser = Parser()
        parser.set_language(GO_LANGUAGE)
        tree = parser.parse(bytes(source_code, 'utf8'))

        module_entity = ModuleEntity(filepath, docstring=None)

        root_node = tree.root_node
        self._parse_node(root_node, module_entity, filepath)

        return module_entity

    def _parse_node(self, node, module_entity, filepath):
        for child in node.children:
            if child.type == 'function_declaration':
                function_entity = self._parse_function(child, filepath)
                module_entity.add_function(function_entity)
            elif child.type == 'type_declaration':
                class_entity = self._parse_type(child, filepath)
                module_entity.add_class(class_entity)
            else:
                self._parse_node(child, module_entity, filepath)

    def _parse_function(self, node, filepath):
        name = None
        signature = None
        docstring = None

        for child in node.children:
            if child.type == 'identifier':
                name = child.text.decode('utf-8')
            elif child.type == 'parameter_list':
                signature = child.text.decode('utf-8')

        return FunctionEntity(name=name, docstring=docstring, signature=signature, file_path=filepath)

    def _parse_type(self, node, filepath):
        name = None
        docstring = None
        methods = {}

        for child in node.children:
            if child.type == 'type_spec':
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        name = grandchild.text.decode('utf-8')
                    elif grandchild.type == 'type':
                        # Handle struct types
                        if grandchild.children[0].type == 'struct_type':
                            struct_node = grandchild.children[0]
                            methods = self._parse_struct(struct_node, filepath)

        return ClassEntity(class_name=name, docstring=docstring, file_path=filepath, methods=methods)

    def _parse_struct(self, node, filepath):
        methods = {}
        # Go structs do not contain methods directly; methods are associated via receiver functions
        # Implement logic to link methods to structs if needed
        return methods