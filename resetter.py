#!/usr/bin/env python3

import os
import sys
from typing import Dict, List, Any, Tuple

from core import get_config, save_config, set_cc_patterns

def reset_claude_ignore_patterns(
    interactive: bool = False, 
    dry_run: bool = False, 
    verbosity: int = 1
) -> Tuple[int, int]:
    """
    Reset Claude Code's ignorePatterns for all directories in ever_touched.
    
    Args:
        interactive: If True, ask for confirmation for each directory
        dry_run: If True, don't actually make changes
        verbosity: Verbosity level (0-4)
        
    Returns:
        Tuple of (number of directories reset, number of errors)
    """
    # Get current configuration
    config = get_config()
    
    # Check if ever_touched is empty
    if not config["ever_touched"]:
        if verbosity >= 1:
            print("No directories have been modified by cc_autoignore yet.")
        return 0, 0
    
    # Confirmation for non-interactive reset
    if not interactive and not dry_run:
        print(f"This will reset Claude Code ignorePatterns in {len(config['ever_touched'])} directories:")
        for i, directory in enumerate(config["ever_touched"]):
            if i < 5 or i >= len(config["ever_touched"]) - 5:
                print(f"  {directory}")
            elif i == 5 and len(config["ever_touched"]) > 10:
                print(f"  ... and {len(config['ever_touched']) - 10} more ...")
                
        confirm = input("Are you sure? [y/N]: ").lower()
        if confirm != 'y':
            print("Reset cancelled.")
            return 0, 0
    
    # Track stats
    reset_count = 0
    error_count = 0
    
    # Process each directory in ever_touched
    for directory in list(config["ever_touched"]):
        # Skip directories that no longer exist
        if not os.path.isdir(directory):
            if verbosity >= 2:
                print(f"Skipping non-existent directory: {directory}")
            continue
            
        # Interactive confirmation
        if interactive and not dry_run:
            confirm = input(f"Reset ignorePatterns in {directory}? [y/N]: ").lower()
            if confirm != 'y':
                if verbosity >= 1:
                    print(f"Skipping {directory}")
                continue
        
        # Reset the ignorePatterns to empty list
        if verbosity >= 1:
            print(f"Resetting ignorePatterns in {directory}")
            
        success = set_cc_patterns(directory, [], dry_run)
        
        if success:
            reset_count += 1
        else:
            error_count += 1
    
    # Update ever_touched list if this wasn't a dry run
    if not dry_run and reset_count > 0:
        # Clear the ever_touched list after reset
        config["ever_touched"] = []
        save_config(config)
    
    return reset_count, error_count