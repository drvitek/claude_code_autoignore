#!/usr/bin/env python3

import os
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple

from core import get_config, save_config, find_top_level_gitdir

def compute_file_hash(file_path: str) -> str:
    """Compute an MD5 hash for a file's contents."""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash

def find_gitignore_files(target_dir: str) -> List[str]:
    """
    Recursively find all .gitignore files in the target directory.
    
    Args:
        target_dir: The directory to scan for .gitignore files
        
    Returns:
        A list of absolute paths to .gitignore files
    """
    gitignore_files = []
    
    for root, dirs, files in os.walk(target_dir):
        # Skip .git directories
        if '.git' in dirs:
            dirs.remove('.git')
            
        if '.gitignore' in files:
            gitignore_path = os.path.join(root, '.gitignore')
            gitignore_files.append(gitignore_path)
    
    return sorted(gitignore_files)

def organize_gitignore_files(gitignore_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Organize .gitignore files by their top-level git directory.
    
    Args:
        gitignore_paths: List of paths to .gitignore files
        
    Returns:
        Dictionary mapping top-level directories to dictionaries of
        gitignore paths and their hashes
    """
    organized = {}
    
    for gitignore_path in gitignore_paths:
        # Find the top-level git directory for this .gitignore file
        gitignore_dir = os.path.dirname(gitignore_path)
        top_level_dir = find_top_level_gitdir(gitignore_dir)
        
        # Skip if not in a git repository
        if not top_level_dir:
            continue
            
        # Compute the file hash
        file_hash = compute_file_hash(gitignore_path)
        
        # Add to the organized dictionary
        if top_level_dir not in organized:
            organized[top_level_dir] = {}
            
        organized[top_level_dir][gitignore_path] = file_hash
    
    return organized

def scan_gitignore_files(
    target_dir: Optional[str] = None, 
    verbosity: int = 1
) -> Tuple[int, int]:
    """
    Scan for .gitignore files, compute their hashes, and update the configuration.
    
    Args:
        target_dir: The directory to scan. If None, uses current directory.
        verbosity: Verbosity level
        
    Returns:
        Tuple of (number of top level directories, number of gitignore files)
    """
    if target_dir is None:
        target_dir = os.getcwd()
    
    target_dir = os.path.abspath(target_dir)
    
    # Get the current configuration
    config = get_config()
    
    # Scan for all .gitignore files
    gitignore_files = find_gitignore_files(target_dir)
    
    if not gitignore_files:
        if verbosity >= 1:
            print(f"No .gitignore files found in {target_dir}")
        return 0, 0
    
    # Organize gitignore files by top-level directory
    organized = organize_gitignore_files(gitignore_files)
    
    # Update the configuration
    for top_dir, gitignore_dict in organized.items():
        config["file_index"][top_dir] = gitignore_dict
    
    # Save the updated configuration
    save_config(config)
    
    # Count stats
    top_level_count = len(organized)
    gitignore_count = len(gitignore_files)
    
    if verbosity >= 1:
        print(f"Found {gitignore_count} .gitignore files in {top_level_count} top-level git directories:")
        
        for top_dir, gitignore_dict in organized.items():
            print(f"\n{top_dir}:")
            for gitignore_path in sorted(gitignore_dict.keys()):
                # Show the relative path if possible
                rel_path = os.path.relpath(gitignore_path, top_dir)
                if verbosity >= 2:
                    print(f"  {rel_path} (hash: {gitignore_dict[gitignore_path]})")
                else:
                    print(f"  {rel_path}")
    
    return top_level_count, gitignore_count