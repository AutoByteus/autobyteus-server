from autobyteus_server.codeverse.core.code_parser.base_code_parser import BaseCodeParser
from autobyteus_server.codeverse.core.code_entities.module_entity import ModuleEntity
import javalang
from autobyteus_server.codeverse.core.code_entities.class_entity import ClassEntity
from autobyteus_server.codeverse.core.code_entities.method_entity import MethodEntity
from autobyteus_server.file_explorer.file_reader import FileReader

class JavaCodeParser(BaseCodeParser):
    """
    This class provides functionality to parse Java source code.

    Methods:
        parse_source_code(filepath: str) -> ModuleEntity: Parses the source code from the file at filepath 
                                                          and extracts its classes and methods.
    """

    def parse_source_code(self, filepath: str) -> ModuleEntity:
        """
        Reads and parses the source code from a .java file and extracts its classes and methods.

        Args:
            filepath (str): Path to a .java file.

        Returns:
            A ModuleEntity object containing the file's classes and methods,
            or None if the source_code could not be read or parsed.
        """
        source_code = FileReader.read_file(filepath)
        if source_code is None:
            return None

        try:
            tree = javalang.parse.parse(source_code)
        except javalang.parser.JavaSyntaxError:
            return None

        module_entity = ModuleEntity(filepath, docstring=None)

        # Process classes
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            class_docstring = None  # Java does not have built-in docstrings
            class_entity = ClassEntity(class_name=class_name, docstring=class_docstring, file_path=filepath)
            # Process methods in the class
            for method in node.methods:
                method_name = method.name
                method_signature = str(method.parameters)
                method_docstring = None  # Java does not have built-in docstrings
                method_entity = MethodEntity(name=method_name, docstring=method_docstring, signature=method_signature, file_path=filepath, class_entity=class_entity)
                class_entity.add_method(method_entity)
            module_entity.add_class(class_entity)

        return module_entity