# autobyteus_server/file_explorer/file_reader.py

import os
from typing import Optional


class FileReader:
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        if not os.path.isfile(file_path) or not file_path.endswith('.py'):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except (UnicodeDecodeError, PermissionError):
            # Handle files that cannot be decoded or accessed
            return None
