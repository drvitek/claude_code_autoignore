#!/usr/bin/env python3

import os
import json
import subprocess
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set

# Default config file path
CONFIG_FILEPATH = os.path.expanduser("~/.cc_autoignore_config")

def get_config() -> Dict[str, Any]:
    """
    Get the configuration data from the config file.
    If the file doesn't exist, create a default config.
    
    Returns:
        Dict containing the configuration
    """
    if not os.path.exists(CONFIG_FILEPATH):
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
        return default_config
    
    try:
        with open(CONFIG_FILEPATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Handle corrupted config file
        print(f"Error: Couldn't read config file at {CONFIG_FILEPATH}. Creating default config.")
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
        return default_config

def save_config(config: Dict[str, Any]) -> None:
    """
    Save the configuration data to the config file.
    
    Args:
        config: The configuration dictionary to save
    """
    with open(CONFIG_FILEPATH, 'w') as f:
        json.dump(config, f, indent=2)

def find_top_level_gitdir(path: str) -> Optional[str]:
    """
    Find the top-level git directory for a given path.
    
    Args:
        path: Path to start searching from
    
    Returns:
        Path to the top-level git directory or None if not found
    """
    current_path = os.path.abspath(path)
    
    while current_path != '/':
        git_dir = os.path.join(current_path, '.git')
        if os.path.isdir(git_dir):
            return current_path
        current_path = os.path.dirname(current_path)
    
    return None

def get_gitignore_patterns(file_path: str) -> List[str]:
    """
    Parse a .gitignore file and return its patterns.
    
    Args:
        file_path: Path to the .gitignore file
    
    Returns:
        List of patterns from the file (with comments and empty lines removed)
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    patterns = []
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        # Skip negation patterns (lines starting with !)
        if line.startswith('!'):
            continue
            
        patterns.append(line)
    
    return patterns

def convert_pattern_to_cc_format(pattern: str) -> List[str]:
    """
    Convert a .gitignore pattern to Claude Code ignorePatterns format.
    
    Args:
        pattern: A .gitignore pattern
    
    Returns:
        List of patterns in Claude Code format
    """
    # Remove any leading slash - this is for matching from root in gitignore 
    # but we'll handle this through the full path logic
    if pattern.startswith('/'):
        pattern = pattern.lstrip('/')
    
    # Handle trailing slash case (directories)
    if pattern.endswith('/'):
        # Add both the directory and everything under it
        return [pattern, f"{pattern}**"]
    
    # If it's a file pattern, just return it as-is
    return [pattern]

def make_cc_patterns(config: Dict[str, Any], top_level_dir: str) -> List[str]:
    """
    Create the combined ignorePatterns list for a top-level git directory.
    
    Args:
        config: The configuration dictionary
        top_level_dir: Path to the top-level git directory
    
    Returns:
        List of patterns for Claude Code's ignorePatterns config
    """
    file_index = config["file_index"]
    options = config["options"]
    
    # Skip if the top-level directory is not in our index
    if top_level_dir not in file_index:
        return []
    
    # Combine patterns from all .gitignore files
    all_patterns: Set[str] = set()
    
    # Process all nested .gitignore files
    for gitignore_path in file_index[top_level_dir]:
        patterns = get_gitignore_patterns(gitignore_path)
        
        # Calculate the relative path from top_level_dir to the gitignore directory
        gitignore_dir = os.path.dirname(gitignore_path)
        rel_path = os.path.relpath(gitignore_dir, top_level_dir)
        
        # If we're at the top level, rel_path will be "."
        prefix = "" if rel_path == "." else f"{rel_path}/"
        
        for pattern in patterns:
            # Skip patterns in the always_remove list
            if pattern in options["always_remove"]:
                continue
                
            # Convert and add the pattern
            for cc_pattern in convert_pattern_to_cc_format(pattern):
                # Add the prefix if the pattern doesn't already start with /
                if not cc_pattern.startswith('/'):
                    prefixed_pattern = f"{prefix}{cc_pattern}"
                else:
                    # If it starts with /, it's already an absolute path from the repo root
                    prefixed_pattern = cc_pattern.lstrip('/')
                
                all_patterns.add(prefixed_pattern)
    
    # Add the always_add patterns
    for pattern in options["always_add"]:
        all_patterns.add(pattern)
    
    return sorted(list(all_patterns))

def get_cc_patterns(dir_path: str) -> List[str]:
    """
    Get the current Claude Code ignorePatterns configuration.
    
    Args:
        dir_path: Directory to get config from
    
    Returns:
        List of patterns from Claude Code's ignorePatterns config
    """
    try:
        result = subprocess.run(
            ["claude", "config", "get", "ignorePatterns"],
            cwd=dir_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output
        patterns_json = result.stdout.strip()
        if not patterns_json:
            return []
            
        patterns = json.loads(patterns_json)
        return patterns
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error getting Claude Code ignorePatterns: {e}")
        return []

def is_patterns_different(current_patterns: List[str], new_patterns: List[str]) -> bool:
    """
    Check if the current and new patterns are different.
    
    Args:
        current_patterns: The current ignorePatterns in Claude Code
        new_patterns: The new patterns to be set
        
    Returns:
        True if patterns are different, False otherwise
    """
    # Convert to sets for comparison, ignore order
    current_set = set(current_patterns)
    new_set = set(new_patterns)
    
    return current_set != new_set

def set_cc_patterns(dir_path: str, patterns: List[str], dry_run: bool = False) -> bool:
    """
    Set the Claude Code ignorePatterns configuration.
    
    Args:
        dir_path: Directory to set config in
        patterns: List of patterns to set
        dry_run: If True, don't actually make changes
    
    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        print(f"Would set ignorePatterns in {dir_path} to:")
        print(json.dumps(patterns, indent=2))
        return True
    
    patterns_json = json.dumps(patterns)
    
    try:
        subprocess.run(
            ["claude", "config", "set", "ignorePatterns", patterns_json],
            cwd=dir_path,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting Claude Code ignorePatterns: {e}")
        return False