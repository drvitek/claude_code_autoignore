#!/usr/bin/env python3

import os
import json
from typing import Dict, List, Any, Tuple, Optional

from core import get_config, make_cc_patterns, get_cc_patterns, is_patterns_different

def check_gitignore_exists(file_path: str) -> bool:
    """
    Check if a .gitignore file still exists.
    
    Args:
        file_path: Path to the .gitignore file
        
    Returns:
        True if the file exists, False otherwise
    """
    return os.path.exists(file_path)

def get_status_for_directory(
    config: Dict[str, Any], 
    top_dir: str, 
    verbosity: int = 1
) -> Tuple[bool, int, int]:
    """
    Get the status for a specific top-level directory.
    
    Args:
        config: The configuration dictionary
        top_dir: Path to the top-level directory
        verbosity: Verbosity level
        
    Returns:
        Tuple of (is_synced, missing_files, total_files)
    """
    file_index = config["file_index"]
    
    # Skip if the directory is not in our index
    if top_dir not in file_index:
        return True, 0, 0
    
    # Check for existence of tracked files
    gitignore_files = list(file_index[top_dir].keys())
    total_files = len(gitignore_files)
    missing_files = sum(1 for f in gitignore_files if not check_gitignore_exists(f))
    
    # Generate the patterns we would set
    expected_patterns = make_cc_patterns(config, top_dir)
    
    # Get the current patterns in Claude Code
    current_patterns = get_cc_patterns(top_dir)
    
    # Check if patterns match
    is_synced = not is_patterns_different(current_patterns, expected_patterns)
    
    if verbosity >= 3:
        if not is_synced:
            print("Expected patterns:")
            print(json.dumps(expected_patterns, indent=2))
            print("Current patterns:")
            print(json.dumps(current_patterns, indent=2))
    
    return is_synced, missing_files, total_files

def report_status(
    target_dir: Optional[str] = None, 
    verbosity: int = 1
) -> Tuple[int, int]:
    """
    Report the status of all tracked .gitignore files.
    
    Args:
        target_dir: Optional directory to filter by
        verbosity: Verbosity level
        
    Returns:
        Tuple of (synced_dirs, unsynced_dirs)
    """
    config = get_config()
    file_index = config["file_index"]
    
    # Filter directories if target_dir is specified
    if target_dir:
        target_dir = os.path.abspath(target_dir)
        top_dirs = [d for d in file_index.keys() if d.startswith(target_dir)]
    else:
        top_dirs = list(file_index.keys())
    
    # Count statistics
    synced_dirs = 0
    unsynced_dirs = 0
    total_files = 0
    missing_files = 0
    
    if not top_dirs:
        print("No tracked .gitignore files found.")
        return 0, 0
    
    # Print header
    print(f"Status for {len(top_dirs)} tracked top-level directories:")
    
    # Check status for each directory
    for top_dir in sorted(top_dirs):
        is_synced, dir_missing, dir_total = get_status_for_directory(
            config, top_dir, verbosity
        )
        
        total_files += dir_total
        missing_files += dir_missing
        
        # Update counters
        if is_synced:
            synced_dirs += 1
            status = "✓" if dir_missing == 0 else "!"
        else:
            unsynced_dirs += 1
            status = "✗"
        
        # Print status line
        if verbosity >= 1:
            file_status = ""
            if dir_missing > 0:
                file_status = f" ({dir_missing}/{dir_total} files missing)"
            
            print(f"{status} {top_dir}{file_status}")
            
            if verbosity >= 2 and not is_synced:
                print("  Claude Code ignorePatterns needs update")
    
    # Print summary
    if verbosity >= 1:
        print(f"\nSummary: {synced_dirs} synced, {unsynced_dirs} unsynced directories")
        if missing_files > 0:
            print(f"Missing files: {missing_files}/{total_files}")
    
    return synced_dirs, unsynced_dirs