import os
import sys
import platform
import pytest
from pathlib import Path

from autobyteus_server.config.app_config import AppConfig


class TestWindowsPathHandling:
    """Tests specifically for Windows path handling edge cases."""

    @pytest.mark.skipif(platform.system() != 'Windows', reason="Windows-specific test")
    def test_windows_escape_sequences(self):
        """Test handling of problematic escape sequences in Windows paths."""
        config = AppConfig()
        
        # Paths with potential escape sequence characters
        test_paths = [
            Path(r"C:\app\logs\app.log"),  # \a could be interpreted as bell
            Path(r"C:\tests\bin\test.log"),  # \b could be interpreted as backspace
            Path(r"C:\temp\files\test.log"),  # \f could be interpreted as form feed
            Path(r"C:\new\reports\test.log"),  # \n could be interpreted as newline
            Path(r"C:\temp\recursive\test.log"),  # \r could be interpreted as carriage return
            Path(r"C:\temp\tabs\test.log"),  # \t could be interpreted as tab
            Path(r"C:\temp\vertical\test.log"),  # \v could be interpreted as vertical tab
        ]
        
        for path in test_paths:
            # Convert to safe string
            safe_path = config._safe_path_string(path)
            
            # Ensure no escape sequences were interpreted
            assert "\a" not in safe_path
            assert "\b" not in safe_path
            assert "\f" not in safe_path
            assert "\n" not in safe_path
            assert "\r" not in safe_path
            assert "\t" not in safe_path
            assert "\v" not in safe_path
            
            # Ensure path can be used for file operations
            # (This is a sanity check that the path is valid)
            try:
                dirname = os.path.dirname(safe_path)
                assert os.path.isabs(dirname)
            except Exception as e:
                pytest.fail(f"Path '{safe_path}' is not valid: {e}")

    @pytest.mark.skipif(platform.system() != 'Windows', reason="Windows-specific test")
    def test_windows_path_joining(self):
        """Test joining paths on Windows."""
        config = AppConfig()
        
        # Test various path combinations
        base_paths = [
            r"C:\Program Files\App",
            r"C:\Users\Test User\Documents",
            r"\\network\share\folder",
            r"C:\temp spaces\logs",
        ]
        
        filenames = [
            "app.log",
            "test file.log",
            "a.log",  # This would trigger \a if not handled correctly
            "report (1).pdf"
        ]
        
        for base in base_paths:
            for filename in filenames:
                base_path = Path(base)
                
                # Method 1: Using Path operator (problematic)
                path1 = str(base_path / filename)
                
                # Method 2: Using safe path handling
                safe_base = config._safe_path_string(base_path)
                path2 = os.path.join(safe_base, filename)
                
                # The paths should be equivalent except for slash style
                assert os.path.normpath(path1) == os.path.normpath(path2)
                
                # But path1 might have interpreted escape sequences if it contains \a, \b, etc.
                if r"\a" in path1 or r"\b" in path1 or r"\f" in path1 or r"\n" in path1 or r"\r" in path1:
                    # Here we would check if there's an actual difference due to escape sequences
                    # This is hard to test directly, so we'll check if the string representation changes
                    original = rf"{base}\{filename}"
                    # If escape sequences were interpreted, the lengths would differ
                    assert len(path2) == len(original.replace("/", "\\"))
