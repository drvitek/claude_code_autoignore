#!/usr/bin/env python3

import os
import json
import pytest
import subprocess
from unittest.mock import patch, MagicMock

# Import the main entry point
import cc_autoignore

class TestCommandLineInterface:
    """Test the command-line interface functionality."""
    
    @patch("argparse.ArgumentParser.parse_args")
    @patch("cc_autoignore.scan_gitignore_files")
    def test_scan_command(self, mock_scan, mock_parse_args, mock_git_repo):
        """Test the scan command."""
        # Configure mock args
        mock_args = MagicMock()
        mock_args.command = "scan"
        mock_args.target = mock_git_repo
        mock_args.verbose = 1
        mock_parse_args.return_value = mock_args
        
        # Configure scan to return some test values
        mock_scan.return_value = (1, 3)  # 1 top-level dir, 3 files
        
        # Run the command
        cc_autoignore.main()
        
        # Check that scan was called with the correct arguments
        mock_scan.assert_called_once_with(mock_git_repo, 3)  # base verbosity 2 + arg verbosity 1
    
    @patch("argparse.ArgumentParser.parse_args")
    @patch("cc_autoignore.report_status")
    def test_status_command(self, mock_status, mock_parse_args, mock_git_repo):
        """Test the status command."""
        # Configure mock args
        mock_args = MagicMock()
        mock_args.command = "status"
        mock_args.target = mock_git_repo
        mock_args.verbose = 0
        mock_parse_args.return_value = mock_args
        
        # Configure status to return some test values
        mock_status.return_value = (1, 0)  # 1 synced, 0 unsynced
        
        # Run the command
        cc_autoignore.main()
        
        # Check that status was called with the correct arguments
        mock_status.assert_called_once_with(mock_git_repo, 2)  # base verbosity 2 + arg verbosity 0
    
    @patch("argparse.ArgumentParser.parse_args")
    @patch("cc_autoignore.update_claude_ignore_patterns")
    def test_update_command(self, mock_update, mock_parse_args, mock_git_repo):
        """Test the update command."""
        # Configure mock args
        mock_args = MagicMock()
        mock_args.command = "update"
        mock_args.target = mock_git_repo
        mock_args.dry_run = True
        mock_args.verbose = 2
        mock_parse_args.return_value = mock_args
        
        # Configure update to return some test values
        mock_update.return_value = (1, 0)  # 1 updated, 0 errors
        
        # Run the command
        cc_autoignore.main()
        
        # Check that update was called with the correct arguments
        mock_update.assert_called_once_with(mock_git_repo, True, 4)  # base verbosity 2 + arg verbosity 2
    
    @patch("argparse.ArgumentParser.parse_args")
    @patch("cc_autoignore.reset_claude_ignore_patterns")
    def test_reset_command(self, mock_reset, mock_parse_args):
        """Test the reset command."""
        # Configure mock args
        mock_args = MagicMock()
        mock_args.command = "reset"
        mock_args.interactive = True
        mock_args.dry_run = False
        mock_args.verbose = 0
        mock_parse_args.return_value = mock_args
        
        # Configure reset to return some test values
        mock_reset.return_value = (2, 0)  # 2 reset, 0 errors
        
        # Run the command
        cc_autoignore.main()
        
        # Check that reset was called with the correct arguments
        mock_reset.assert_called_once_with(True, False, 2)  # base verbosity 2 + arg verbosity 0
    
    @patch("argparse.ArgumentParser.parse_args")
    @patch("cc_autoignore.get_config_value")
    def test_config_get_command(self, mock_get_value, mock_parse_args):
        """Test the config get command."""
        # Configure mock args
        mock_args = MagicMock()
        mock_args.command = "config"
        mock_args.config_command = "get"
        mock_args.option = "options.verbosity"
        mock_parse_args.return_value = mock_args
        
        # Configure get_value to return a test value
        mock_get_value.return_value = 1
        
        # Run the command
        cc_autoignore.main()
        
        # Check that get_value was called with the correct argument
        mock_get_value.assert_called_once_with("options.verbosity")
    
    @patch("argparse.ArgumentParser.parse_args")
    @patch("cc_autoignore.set_config_value")
    def test_config_set_command(self, mock_set_value, mock_parse_args):
        """Test the config set command."""
        # Configure mock args
        mock_args = MagicMock()
        mock_args.command = "config"
        mock_args.config_command = "set"
        mock_args.option = "options.verbosity"
        mock_args.value = "2"
        mock_parse_args.return_value = mock_args
        
        # Configure set_value to return success
        mock_set_value.return_value = True
        
        # Run the command
        cc_autoignore.main()
        
        # Check that set_value was called with the correct arguments
        mock_set_value.assert_called_once_with("options.verbosity", 2)  # Should convert to int
    
    @patch("argparse.ArgumentParser.parse_args")
    @patch("cc_autoignore.update_config_list")
    def test_config_add_command(self, mock_update_list, mock_parse_args):
        """Test the config add command."""
        # Configure mock args
        mock_args = MagicMock()
        mock_args.command = "config"
        mock_args.config_command = "add"
        mock_args.option = "options.always_add"
        mock_args.values = ["node_modules/", "dist/"]
        mock_parse_args.return_value = mock_args
        
        # Configure update_list to return success
        mock_update_list.return_value = True
        
        # Run the command
        cc_autoignore.main()
        
        # Check that update_list was called with the correct arguments
        mock_update_list.assert_called_once_with("options.always_add", ["node_modules/", "dist/"], remove=False)