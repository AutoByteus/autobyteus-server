from autobyteus_server.codeverse.core.code_parser.base_code_parser import BaseCodeParser
from autobyteus_server.codeverse.core.code_entities.module_entity import ModuleEntity
import ast
from autobyteus_server.codeverse.core.code_parser.python_ast_node_visitor import PythonAstNodeVisitor
from autobyteus_server.file_explorer.file_reader import FileReader

class PythonCodeParser(BaseCodeParser):
    """
    This class provides functionality to parse Python source code.

    Methods:
        parse_source_code(filepath: str) -> ModuleEntity: Parses the source code from the file at filepath 
                                                          and extracts its docstring, functions, and classes.
    """

    def parse_source_code(self, filepath: str) -> ModuleEntity:
        """
        Reads and parses the source code from a .py file and extracts its docstring, functions and classes.

        Args:
            filepath (str): Path to a .py file.

        Returns:
            A ModuleEntity object containing the file's docstring, functions and classes,
            or None if the source_code could not be read or parsed.
        """
        source_code = FileReader.read_file(filepath)
        if source_code is None:
            return None

        module = ast.parse(source_code)
        visitor = PythonAstNodeVisitor(filepath)

        module_entity = ModuleEntity(filepath, ast.get_docstring(module))

        functions = [visitor.visit(n) for n in module.body if isinstance(n, ast.FunctionDef)]
        classes = [visitor.visit(n) for n in module.body if isinstance(n, ast.ClassDef)]
        
        for function in functions:
            module_entity.add_function(function)

        for class_ in classes:
            module_entity.add_class(class_)

        return module_entity