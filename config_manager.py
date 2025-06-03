"""
Configuration management for the CardMarket scraper.
Handles loading and validating YAML configuration files.
"""

import yaml
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self):
        self.config = None
    
    def load_config(self, config_file: str) -> Optional[Dict[str, Any]]:
        """
        Load YAML configuration file.
        
        Args:
            config_file: Path to the YAML configuration file
            
        Returns:
            Dictionary containing configuration data, or None if failed
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            print(f"✅ Loaded config from {config_file}")
            return self.config
        except FileNotFoundError:
            print(f"❌ Config file not found: {config_file}")
            return None
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate that the configuration has required fields.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not config:
            print("❌ Config is empty")
            return False
        
        if 'name' not in config:
            print("❌ Config must have 'name' field")
            return False
        
        if 'cards' not in config:
            print("❌ Config must have 'cards' field")
            return False
        
        if not isinstance(config['cards'], dict):
            print("❌ 'cards' field must be a dictionary")
            return False
        
        if not config['cards']:
            print("❌ 'cards' dictionary cannot be empty")
            return False
        
        print("✅ Configuration is valid")
        return True
    
    def get_wait_time(self, config: Dict[str, Any]) -> int:
        """
        Get wait time from config, with default fallback.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Wait time in seconds
        """
        return config.get('wait_time', 3)
    
    def get_list_name(self, config: Dict[str, Any]) -> str:
        """
        Get list name from config.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List name string
        """
        return config.get('name', 'Unknown List')
    
    def get_cards(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get cards dictionary from config.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary of cards and their configurations
        """
        return config.get('cards', {})
