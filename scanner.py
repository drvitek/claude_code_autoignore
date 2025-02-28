#!/usr/bin/env python3

import os
import hashlib
import argparse
from typing import Dict, List, Optional


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


def scan_gitignore_files(target_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Scan for .gitignore files and compute their hashes.
    
    Args:
        target_dir: The directory to scan. If None, uses current directory.
        
    Returns:
        A dictionary mapping file paths to their MD5 hashes
    """
    if target_dir is None:
        target_dir = os.getcwd()
    
    target_dir = os.path.abspath(target_dir)
    
    gitignore_files = find_gitignore_files(target_dir)
    result = {}
    
    for file_path in gitignore_files:
        file_hash = compute_file_hash(file_path)
        result[file_path] = file_hash
    
    return result


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the scanner module."""
    parser = argparse.ArgumentParser(
        description="Scan for .gitignore files to sync with Claude Code"
    )
    
    parser.add_argument(
        "--target", 
        type=str,
        default=os.getcwd(),
        help="Target directory to scan for .gitignore files (default: current directory)"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point when run as a script."""
    args = parse_args()
    gitignore_files = scan_gitignore_files(args.target)
    
    if not gitignore_files:
        print(f"No .gitignore files found in {args.target}")
        return
    
    print(f"Found {len(gitignore_files)} .gitignore files:")
    for file_path, file_hash in gitignore_files.items():
        print(f"  {file_path} (hash: {file_hash})")


if __name__ == "__main__":
    main()