import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class Settings:
    def __init__(self):
        self.instances = self._load_openai_instances()
        
    def _load_openai_instances(self) -> List[Dict[str, str]]:
        """
        Load OpenAI instances configuration from environment variables or external config file.
        Priority order:
        1. OPENAI_INSTANCES environment variable (JSON string)
        2. OPENAI_CONFIG_PATH environment variable (path to JSON file)
        3. Default config file at /config/openai_instances.json
        """
        # Try to load from OPENAI_INSTANCES environment variable
        instances_json = os.environ.get("OPENAI_INSTANCES")
        if instances_json:
            try:
                instances_data = json.loads(instances_json)
                return instances_data.get("instances", [])
            except json.JSONDecodeError:
                print("Error: OPENAI_INSTANCES environment variable contains invalid JSON")
        
        # Try to load from config file path specified in environment variable
        config_path = os.environ.get("OPENAI_CONFIG_PATH")
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        instances_data = json.load(f)
                        return instances_data.get("instances", [])
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading config from {config_path}: {e}")
        
        # Try default config paths
        default_paths = [
            Path("/config/openai_instances.json"),  # Container path
            Path("./config/openai_instances.json"),  # Local dev path
            Path(os.path.dirname(__file__)).parent.parent.parent / "config" / "openai_instances.json"  # Project root
        ]
        
        for path in default_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        instances_data = json.load(f)
                        return instances_data.get("instances", [])
                except (json.JSONDecodeError, IOError):
                    continue
                
        # If no configuration is found, return empty list
        print("Warning: No OpenAI instances configuration found")
        return []

    def get_log_level(self) -> str:
        """Get log level from environment variable or default to INFO"""
        return os.environ.get("LOG_LEVEL", "INFO")

    def get_log_file(self) -> Optional[str]:
        """Get log file path from environment variable"""
        return os.environ.get("LOG_FILE")


# Create a global settings instance
settings = Settings()