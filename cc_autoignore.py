#!/usr/bin/env python3

import os
import sys
import argparse
from typing import List, Optional

# Import functions from scanner module
from scanner import scan_gitignore_files


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Utility for synchronizing Claude Code's ignore configuration with .gitignore patterns."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for .gitignore files")
    scan_parser.add_argument(
        "--target",
        type=str,
        default=os.getcwd(),
        help="Target directory to scan (default: current directory)"
    )
    
    # Status command placeholder
    subparsers.add_parser("status", help="View status of tracked .gitignore files")
    
    # Update command placeholder
    update_parser = subparsers.add_parser("update", help="Update Claude Code ignore patterns")
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    
    # Reset command placeholder
    subparsers.add_parser("reset", help="Reset all Claude Code ignore patterns set by the tool")
    
    return parser.parse_args()


def handle_scan_command(target_dir: Optional[str] = None) -> None:
    """
    Handle the scan command.
    
    Args:
        target_dir: Directory to scan for .gitignore files
    """
    gitignore_files = scan_gitignore_files(target_dir)
    
    if not gitignore_files:
        print(f"No .gitignore files found in {target_dir}")
        return
    
    print(f"Found {len(gitignore_files)} .gitignore files:")
    for file_path, file_hash in gitignore_files.items():
        print(f"  {file_path} (hash: {file_hash})")


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    if args.command == "scan":
        handle_scan_command(args.target)
    elif args.command == "status":
        print("Status command not implemented yet")
    elif args.command == "update":
        print("Update command not implemented yet")
        if args.dry_run:
            print("(Dry run mode)")
    elif args.command == "reset":
        print("Reset command not implemented yet")
    else:
        print("Please specify a command. Run with --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()