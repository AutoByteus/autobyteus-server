from autobyteus_server.codeverse.core.code_parser.base_code_parser import BaseCodeParser
from autobyteus_server.codeverse.core.code_parser.python_code_parser import PythonCodeParser
from autobyteus_server.codeverse.core.code_parser.java_code_parser import JavaCodeParser
# from autobyteus_server.codeverse.core.code_parser.go_code_parser import GoCodeParser
# from autobyteus_server.codeverse.core.code_parser.javascript_code_parser import JavaScriptCodeParser

class CodeParserFactory:
    @staticmethod
    def get_parser(language: str) -> BaseCodeParser:
        if language.lower() == 'python':
            return PythonCodeParser()
        elif language.lower() == 'java':
            return JavaCodeParser()
        # elif language.lower() == 'go':
        #     return GoCodeParser()
        # elif language.lower() == 'javascript':
        #     return JavaScriptCodeParser()
        else:
            raise ValueError(f"No parser available for language: {language}")