#!/usr/bin/env python3

import os
import sys
import argparse
from typing import List, Optional, Any

# Import modules
from core import get_config
from scanner import scan_gitignore_files
from updater import update_claude_ignore_patterns
from resetter import reset_claude_ignore_patterns
from status_reporter import report_status
from config_manager import (
    get_config_value, 
    set_config_value,
    update_config_list,
    list_config,
    reset_config
)


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
    scan_parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (can be used multiple times)"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="View status of tracked .gitignore files")
    status_parser.add_argument(
        "--target",
        type=str,
        help="Filter status to a specific directory"
    )
    status_parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (can be used multiple times)"
    )
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update Claude Code ignore patterns")
    update_parser.add_argument(
        "--target",
        type=str,
        default=os.getcwd(),
        help="Target directory to update (default: current directory)"
    )
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    update_parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (can be used multiple times)"
    )
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset all Claude Code ignore patterns set by the tool")
    reset_parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive reset (confirm each directory)"
    )
    reset_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    reset_parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (can be used multiple times)"
    )
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config command to execute")
    
    # Config get
    config_get_parser = config_subparsers.add_parser("get", help="Get a configuration value")
    config_get_parser.add_argument(
        "option",
        type=str,
        help="Option name to get (e.g., 'options.verbosity')"
    )
    
    # Config set
    config_set_parser = config_subparsers.add_parser("set", help="Set a configuration value")
    config_set_parser.add_argument(
        "option",
        type=str,
        help="Option name to set (e.g., 'options.verbosity')"
    )
    config_set_parser.add_argument(
        "value",
        help="Value to set"
    )
    
    # Config add
    config_add_parser = config_subparsers.add_parser("add", help="Add values to a list option")
    config_add_parser.add_argument(
        "option",
        type=str,
        help="List option name (e.g., 'options.always_add')"
    )
    config_add_parser.add_argument(
        "values",
        nargs="+",
        help="Values to add to the list"
    )
    
    # Config remove
    config_remove_parser = config_subparsers.add_parser("remove", help="Remove values from a list option")
    config_remove_parser.add_argument(
        "option",
        type=str,
        help="List option name (e.g., 'options.always_remove')"
    )
    config_remove_parser.add_argument(
        "values",
        nargs="+",
        help="Values to remove from the list"
    )
    
    # Config list
    config_subparsers.add_parser("list", help="List all configuration")
    
    # Config reset
    config_subparsers.add_parser("reset", help="Reset configuration to defaults")
    
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Get config to initialize
    config = get_config()
    
    # Get the base verbosity from config
    base_verbosity = config["options"].get("verbosity", 1)
    
    if args.command == "scan":
        # Adjust verbosity based on command line flags
        verbosity = base_verbosity
        if hasattr(args, 'verbose'):
            verbosity += args.verbose
            
        scan_gitignore_files(args.target, verbosity)
    elif args.command == "status":
        # Adjust verbosity based on command line flags
        verbosity = base_verbosity
        if hasattr(args, 'verbose'):
            verbosity += args.verbose
            
        report_status(args.target, verbosity)
    elif args.command == "update":
        # Adjust verbosity based on command line flags
        verbosity = base_verbosity
        if hasattr(args, 'verbose'):
            verbosity += args.verbose
            
        updated, errors = update_claude_ignore_patterns(args.target, args.dry_run, verbosity)
        
        if verbosity >= 1:
            print(f"\nSummary: {updated} directories updated, {errors} errors")
    elif args.command == "reset":
        # Adjust verbosity based on command line flags
        verbosity = base_verbosity
        if hasattr(args, 'verbose'):
            verbosity += args.verbose
            
        reset, errors = reset_claude_ignore_patterns(args.interactive, args.dry_run, verbosity)
        
        if verbosity >= 1 and (reset > 0 or errors > 0):
            print(f"\nSummary: {reset} directories reset, {errors} errors")
    elif args.command == "config":
        if not args.config_command:
            print("Please specify a config command. Run with --help for usage information.")
            sys.exit(1)
            
        if args.config_command == "get":
            value = get_config_value(args.option)
            if value is not None:
                # Pretty print the value based on its type
                if isinstance(value, (list, dict)):
                    import json
                    print(json.dumps(value, indent=2))
                else:
                    print(value)
            else:
                print(f"Option '{args.option}' not found")
                sys.exit(1)
        elif args.config_command == "set":
            # Try to parse the value as an integer or boolean
            try:
                # Check if it's an integer
                value = int(args.value)
            except ValueError:
                # Check if it's a boolean
                if args.value.lower() == 'true':
                    value = True
                elif args.value.lower() == 'false':
                    value = False
                else:
                    # Keep it as a string
                    value = args.value
                    
            success = set_config_value(args.option, value)
            if success:
                print(f"Set '{args.option}' to '{value}'")
            else:
                print(f"Failed to set '{args.option}'")
                sys.exit(1)
        elif args.config_command == "add":
            success = update_config_list(args.option, args.values, remove=False)
            if success:
                print(f"Added values to '{args.option}'")
            else:
                print(f"Failed to add values to '{args.option}'")
                sys.exit(1)
        elif args.config_command == "remove":
            success = update_config_list(args.option, args.values, remove=True)
            if success:
                print(f"Removed values from '{args.option}'")
            else:
                print(f"Failed to remove values from '{args.option}'")
                sys.exit(1)
        elif args.config_command == "list":
            import json
            print(json.dumps(list_config(), indent=2))
        elif args.config_command == "reset":
            reset_config()
            print("Configuration reset to defaults")
    else:
        print("Please specify a command. Run with --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()