#!/usr/bin/env python3

import os
from typing import Dict, List, Any, Optional, Tuple

from core import get_config, save_config

def get_config_value(option_name: str) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        option_name: Name of the option to retrieve
        
    Returns:
        The value of the option, or None if it doesn't exist
    """
    config = get_config()
    
    # Handle option path with dot notation (e.g., "options.verbosity")
    if '.' in option_name:
        parts = option_name.split('.')
        current = config
        
        for part in parts:
            if part not in current:
                return None
            current = current[part]
            
        return current
    
    # Direct top-level option
    return config.get(option_name)

def set_config_value(option_name: str, value: Any) -> bool:
    """
    Set a specific configuration value.
    
    Args:
        option_name: Name of the option to set
        value: Value to set
        
    Returns:
        True if successful, False otherwise
    """
    config = get_config()
    
    # Handle option path with dot notation (e.g., "options.verbosity")
    if '.' in option_name:
        parts = option_name.split('.')
        current = config
        
        # Navigate to the deepest level
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                # Create missing dictionaries if they don't exist
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Can't navigate further if it's not a dict
                return False
                
            current = current[part]
        
        # Set the value at the deepest level
        current[parts[-1]] = value
    else:
        # Direct top-level option
        config[option_name] = value
    
    # Save the updated config
    save_config(config)
    return True

def update_config_list(option_name: str, values: List[str], remove: bool = False) -> bool:
    """
    Add or remove values from a list option.
    
    Args:
        option_name: Name of the list option to update
        values: Values to add or remove
        remove: If True, remove values; if False, add values
        
    Returns:
        True if successful, False otherwise
    """
    current_value = get_config_value(option_name)
    
    # Ensure the option exists and is a list
    if current_value is None:
        if remove:
            # Nothing to remove from if it doesn't exist
            return True
        else:
            # Create a new list with the values
            return set_config_value(option_name, values)
    
    if not isinstance(current_value, list):
        return False
    
    # Update the list
    updated_list = current_value.copy()
    
    if remove:
        # Remove values
        updated_list = [item for item in updated_list if item not in values]
    else:
        # Add values (avoid duplicates)
        for value in values:
            if value not in updated_list:
                updated_list.append(value)
    
    # Save the updated list
    return set_config_value(option_name, updated_list)

def list_config() -> Dict[str, Any]:
    """
    Get the entire configuration.
    
    Returns:
        The full configuration dictionary
    """
    return get_config()

def reset_config() -> bool:
    """
    Reset the configuration to default values.
    
    Returns:
        True if successful
    """
    default_config = {
        "file_index": {},
        "ever_touched": [],
        "options": {
            "verbosity": 1,
            "always_add": [],
            "always_remove": []
        }
    }
    
    save_config(default_config)
    return True