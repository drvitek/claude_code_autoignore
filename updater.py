#!/usr/bin/env python3

import os
from typing import Dict, List, Any, Set, Tuple
import hashlib

from core import (
    get_config, 
    save_config, 
    make_cc_patterns, 
    get_cc_patterns, 
    set_cc_patterns,
    find_top_level_gitdir
)

def compute_file_hash(file_path: str) -> str:
    """Compute an MD5 hash for a file's contents."""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash

def find_changed_gitignores(config: Dict[str, Any]) -> Set[str]:
    """
    Find all .gitignore files that have changed since last update.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        Set of top-level git directories with changed .gitignore files
    """
    file_index = config["file_index"]
    changed_top_dirs = set()
    
    # Check all tracked .gitignore files for changes
    for top_dir, gitignore_dict in file_index.items():
        has_changes = False
        
        # Track if any gitignore file has changed or been deleted
        for gitignore_path, stored_hash in gitignore_dict.items():
            # Check if the file still exists
            if not os.path.exists(gitignore_path):
                has_changes = True
                continue
                
            # Compare stored hash with current hash
            current_hash = compute_file_hash(gitignore_path)
            if current_hash != stored_hash:
                has_changes = True
                
        if has_changes:
            changed_top_dirs.add(top_dir)
            
    return changed_top_dirs

def update_gitignore_hashes(config: Dict[str, Any], top_dir: str) -> Dict[str, Any]:
    """
    Update the stored hashes for all .gitignore files in a top-level directory.
    
    Args:
        config: The configuration dictionary
        top_dir: The top-level directory to update
        
    Returns:
        Updated configuration dictionary
    """
    file_index = config["file_index"]
    
    # Update hashes for all existing files
    if top_dir in file_index:
        updated_dict = {}
        for gitignore_path in file_index[top_dir]:
            if os.path.exists(gitignore_path):
                updated_dict[gitignore_path] = compute_file_hash(gitignore_path)
                
        # Replace the old dict with updated one
        file_index[top_dir] = updated_dict
        
    return config

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

def update_claude_ignore_patterns(
    target_dir: str, 
    dry_run: bool = False, 
    verbosity: int = 1
) -> Tuple[int, int]:
    """
    Update Claude Code's ignorePatterns for all changed .gitignore files.
    
    Args:
        target_dir: Directory to update
        dry_run: If True, don't actually make changes
        verbosity: Verbosity level (0-4)
        
    Returns:
        Tuple of (number of directories updated, number of directories with errors)
    """
    # Get current configuration
    config = get_config()
    
    # Find all top-level git directories with changes
    changed_dirs = find_changed_gitignores(config)
    
    # Filter to only include those under target_dir
    target_dir = os.path.abspath(target_dir)
    changed_dirs = {d for d in changed_dirs if d.startswith(target_dir)}
    
    # Track stats
    updated = 0
    errors = 0
    
    # Track directories we've touched for the ever_touched list
    touched_dirs = set()
    
    for top_dir in changed_dirs:
        # Generate new patterns
        new_patterns = make_cc_patterns(config, top_dir)
        
        # Get current patterns
        current_patterns = get_cc_patterns(top_dir)
        
        # Check if patterns are different
        if not is_patterns_different(current_patterns, new_patterns):
            if verbosity >= 2:
                print(f"No pattern changes needed for {top_dir}")
            
            # Still update hashes to reflect current state
            config = update_gitignore_hashes(config, top_dir)
            continue
            
        # Update Claude Code's ignorePatterns
        if verbosity >= 1:
            print(f"Updating ignorePatterns for {top_dir}")
            
        if verbosity >= 3:
            print("  Current patterns:", current_patterns)
            print("  New patterns:", new_patterns)
            
        success = set_cc_patterns(top_dir, new_patterns, dry_run)
        
        if success:
            updated += 1
            touched_dirs.add(top_dir)
            
            # Update hashes to reflect current state
            if not dry_run:
                config = update_gitignore_hashes(config, top_dir)
        else:
            errors += 1
    
    # Update ever_touched list if this wasn't a dry run
    if not dry_run and touched_dirs:
        for dir_path in touched_dirs:
            if dir_path not in config["ever_touched"]:
                config["ever_touched"].append(dir_path)
        
        # Save updated config
        save_config(config)
    
    return updated, errors