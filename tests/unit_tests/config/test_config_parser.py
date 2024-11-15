import pytest
from unittest.mock import mock_open, patch
from autobyteus_server.config.config_parser import ConfigParser, YAMLConfigParser, TOMLConfigParser, ENVConfigParser

# Sample config contents
YAML_CONTENT = """
key1: value1
key2: value2
"""

TOML_CONTENT = """
key1 = "value1"
key2 = "value2"
"""

ENV_CONTENT = """
KEY1=value1
KEY2=value2
"""

@pytest.fixture
def sample_yaml_file(tmp_path):
    file = tmp_path / "config.yaml"
    file.write_text(YAML_CONTENT)
    return str(file)

@pytest.fixture
def sample_toml_file(tmp_path):
    file = tmp_path / "config.toml"
    file.write_text(TOML_CONTENT)
    return str(file)

@pytest.fixture
def sample_env_file(tmp_path):
    file = tmp_path / "config.env"
    file.write_text(ENV_CONTENT)
    return str(file)

def test_config_parser_abstract():
    with pytest.raises(TypeError):
        ConfigParser()

@pytest.mark.parametrize("parser_class,file_content,expected", [
    (YAMLConfigParser, YAML_CONTENT, {"key1": "value1", "key2": "value2"}),
    (TOMLConfigParser, TOML_CONTENT, {"key1": "value1", "key2": "value2"}),
    (ENVConfigParser, ENV_CONTENT, {"KEY1": "value1", "KEY2": "value2"}),
])
def test_parser_parse(parser_class, file_content, expected):
    parser = parser_class()
    with patch("builtins.open", mock_open(read_data=file_content)):
        result = parser.parse("dummy_file")
    assert result == expected

def test_yaml_parser_file_not_found():
    parser = YAMLConfigParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("non_existent_file.yaml")

def test_toml_parser_file_not_found():
    parser = TOMLConfigParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("non_existent_file.toml")

def test_env_parser_file_not_found():
    parser = ENVConfigParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("non_existent_file.env")

@pytest.mark.parametrize("parser_class,file_content", [
    (YAMLConfigParser, "invalid: yaml: content:"),
    (TOMLConfigParser, "invalid toml content"),
])
def test_parser_invalid_content(parser_class, file_content):
    parser = parser_class()
    with patch("builtins.open", mock_open(read_data=file_content)):
        with pytest.raises(Exception):  # Specific exception types may vary
            parser.parse("dummy_file")

def test_parser_empty_file():
    for parser_class in [YAMLConfigParser, TOMLConfigParser, ENVConfigParser]:
        parser = parser_class()
        with patch("builtins.open", mock_open(read_data="")):
            result = parser.parse("dummy_file")
        assert result == {}

# Integration tests with actual file operations
def test_yaml_parser_integration(sample_yaml_file):
    parser = YAMLConfigParser()
    result = parser.parse(sample_yaml_file)
    assert result == {"key1": "value1", "key2": "value2"}

def test_toml_parser_integration(sample_toml_file):
    parser = TOMLConfigParser()
    result = parser.parse(sample_toml_file)
    assert result == {"key1": "value1", "key2": "value2"}

def test_env_parser_integration(sample_env_file):
    parser = ENVConfigParser()
    result = parser.parse(sample_env_file)
    assert result == {"KEY1": "value1", "KEY2": "value2"}