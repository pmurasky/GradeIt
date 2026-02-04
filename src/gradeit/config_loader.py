"""
Configuration loader for GradeIt.
Handles loading and parsing config.properties with variable substitution.
"""

import re
from pathlib import Path
from typing import Dict, Optional


class ConfigLoader:
    """Loads and manages configuration from properties file."""
    
    def __init__(self, config_path: str):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to the config.properties file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, str] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from the properties file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        raw_config: Dict[str, str] = {}
        
        # First pass: read all key-value pairs
        with open(self.config_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    raw_config[key.strip()] = value.strip()
        
        # Second pass: resolve variable substitutions
        self.config = self._resolve_variables(raw_config)
    
    def _resolve_variables(self, raw_config: Dict[str, str]) -> Dict[str, str]:
        """
        Resolve variable substitutions like ${base_directory}.
        
        Args:
            raw_config: Raw configuration dictionary
            
        Returns:
            Configuration with resolved variables
        """
        resolved = {}
        max_iterations = 10  # Prevent infinite loops
        
        for iteration in range(max_iterations):
            all_resolved = True
            
            for key, value in raw_config.items():
                # Find all ${variable} patterns
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, value)
                
                if matches:
                    all_resolved = False
                    # Replace each variable reference
                    for var_name in matches:
                        if var_name in resolved:
                            value = value.replace(f'${{{var_name}}}', resolved[var_name])
                        elif var_name in raw_config:
                            # Use raw value if not yet resolved
                            value = value.replace(f'${{{var_name}}}', raw_config[var_name])
                
                resolved[key] = value
            
            # Update raw_config for next iteration
            raw_config = resolved.copy()
            
            if all_resolved:
                break
        
        return resolved
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get a configuration value as an integer.
        
        Args:
            key: Configuration key
            default: Default value if key not found or invalid
            
        Returns:
            Configuration value as integer
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            return default
    
    def get_path(self, key: str) -> Optional[Path]:
        """
        Get a configuration value as a Path object.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value as Path or None
        """
        value = self.get(key)
        return Path(value) if value else None
    
    def __repr__(self) -> str:
        """String representation of the config."""
        return f"ConfigLoader(config_path='{self.config_path}', keys={list(self.config.keys())})"
