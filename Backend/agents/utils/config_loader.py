"""
Configuration Loader Utility
Loads and validates agent configuration from YAML files.
"""
import yaml
import os
from typing import Dict, Any
import logging

logger = logging.getLogger("ConfigLoader")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML configuration file
    
    Returns:
        Configuration dictionary
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"Loaded configuration from {config_path}")
    return config


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate configuration against schema.
    
    Args:
        config: Configuration to validate
        schema: Schema definition
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If validation fails
    """
    # Basic validation - check required keys
    required_sections = schema.get('required_sections', [])
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    logger.info("Configuration validated successfully")
    return True


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.
    Override config takes precedence.
    
    Args:
        base_config: Base configuration
        override_config: Override configuration
    
    Returns:
        Merged configuration
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def load_agent_config(agent_id: str, config_dir: str = "config", common_config_name: str = "common_config.yaml") -> Dict[str, Any]:
    """
    Load agent configuration with common config merging.
    
    Args:
        agent_id: Agent identifier (e.g., "pm_agent")
        config_dir: Directory containing config files
        common_config_name: Name of common configuration file
    
    Returns:
        Complete agent configuration
    """
    # Load common config
    common_config_path = os.path.join(config_dir, common_config_name)
    common_config = {}
    
    if os.path.exists(common_config_path):
        common_config = load_config(common_config_path)
        logger.info(f"Loaded common config from {common_config_path}")
    
    # Load agent-specific config
    agent_config_path = os.path.join(config_dir, f"{agent_id}_config.yaml")
    agent_config = load_config(agent_config_path)
    
    # Merge configurations
    final_config = merge_configs(common_config, agent_config)
    
    logger.info(f"Configuration loaded for {agent_id}")
    return final_config
