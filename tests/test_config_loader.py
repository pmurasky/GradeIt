"""
Unit tests for ConfigLoader
"""

import pytest
import tempfile
from pathlib import Path
from src.gradeit.config_loader import ConfigLoader


class TestConfigLoader:
    """Test cases for ConfigLoader class."""
    
    def test_load_simple_config(self, tmp_path):
        """Test loading a simple configuration file."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("""
# Test config
key1=value1
key2=value2
max_grade=100
        """)
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get('key1') == 'value1'
        assert loader.get('key2') == 'value2'
        assert loader.get_int('max_grade') == 100
    
    def test_variable_substitution(self, tmp_path):
        """Test variable substitution like ${base_directory}."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("""
base_directory=/home/user
students_file=${base_directory}/students.txt
output_directory=${base_directory}/output
        """)
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get('base_directory') == '/home/user'
        assert loader.get('students_file') == '/home/user/students.txt'
        assert loader.get('output_directory') == '/home/user/output'
    
    def test_nested_variable_substitution(self, tmp_path):
        """Test nested variable substitution."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("""
base=/home
user_dir=${base}/user
project_dir=${user_dir}/project
        """)
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get('project_dir') == '/home/user/project'
    
    def test_get_with_default(self, tmp_path):
        """Test get() with default value."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("key1=value1")
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get('key1') == 'value1'
        assert loader.get('nonexistent', 'default') == 'default'
        assert loader.get('nonexistent') is None
    
    def test_get_int(self, tmp_path):
        """Test get_int() method."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("""
max_grade=100
passing_grade=60
invalid=not_a_number
        """)
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get_int('max_grade') == 100
        assert loader.get_int('passing_grade') == 60
        assert loader.get_int('invalid', 0) == 0
        assert loader.get_int('nonexistent', 50) == 50
    
    def test_get_path(self, tmp_path):
        """Test get_path() method."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("directory=/home/user/project")
        
        loader = ConfigLoader(str(config_file))
        
        path = loader.get_path('directory')
        assert isinstance(path, Path)
        assert str(path) == '/home/user/project'
        assert loader.get_path('nonexistent') is None
    
    def test_ignore_comments_and_empty_lines(self, tmp_path):
        """Test that comments and empty lines are ignored."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("""
# This is a comment
key1=value1

# Another comment
key2=value2

        """)
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get('key1') == 'value1'
        assert loader.get('key2') == 'value2'
        assert len(loader.config) == 2
    
    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for missing config."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader('/nonexistent/path/config.properties')
    
    def test_equals_in_value(self, tmp_path):
        """Test handling of equals sign in values."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("url=http://example.com?param=value")
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get('url') == 'http://example.com?param=value'
    
    def test_whitespace_handling(self, tmp_path):
        """Test that whitespace around keys and values is stripped."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("""
  key1  =  value1  
key2=value2
        """)
        
        loader = ConfigLoader(str(config_file))
        
        assert loader.get('key1') == 'value1'
        assert loader.get('key2') == 'value2'
    
    def test_repr(self, tmp_path):
        """Test string representation."""
        config_file = tmp_path / "test.properties"
        config_file.write_text("key1=value1")
        
        loader = ConfigLoader(str(config_file))
        repr_str = repr(loader)
        
        assert 'ConfigLoader' in repr_str
        assert str(config_file) in repr_str
        assert 'key1' in repr_str
