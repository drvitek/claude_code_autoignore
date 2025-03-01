#!/usr/bin/env python3

import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Import modules for testing
from scanner import scan_gitignore_files
from updater import update_claude_ignore_patterns
from status_reporter import report_status
from resetter import reset_claude_ignore_patterns

class TestIntegrationFlow:
    """Test the complete workflow through integration tests."""
    
    @patch("subprocess.run")
    @patch("updater.is_patterns_different")
    @patch("updater.find_changed_gitignores")
    @patch("updater.make_cc_patterns")  # This is the correct module path
    def test_scan_then_update(self, mock_make_patterns, mock_find_changed, mock_is_diff, mock_subprocess, mock_git_repo, setup_mock_config):
        """Test scanning and then updating."""
        # Configure subprocess mock to return empty patterns initially
        mock_subprocess.return_value.stdout = "[]"
        mock_subprocess.return_value.returncode = 0
        
        # Setup config with outdated hashes to trigger change detection
        root_gitignore = os.path.join(mock_git_repo, ".gitignore")
        src_gitignore = os.path.join(mock_git_repo, "src", ".gitignore")
        docs_gitignore = os.path.join(mock_git_repo, "docs", ".gitignore")
        
        # Add files to the file_index
        setup_mock_config["file_index"] = {
            mock_git_repo: {
                root_gitignore: "outdated_hash1",
                src_gitignore: "outdated_hash2",
                docs_gitignore: "outdated_hash3"
            }
        }
        
        # Mock find_changed_gitignores to return our mock_git_repo
        # This simulates that the directory has changed .gitignore files
        mock_find_changed.return_value = {mock_git_repo}
        
        # Force is_patterns_different to return True to trigger an update
        mock_is_diff.return_value = True
        
        # Mock the pattern generation to return known patterns
        expected_patterns = [
            "*.log", "node_modules/", "node_modules/**",
            "src/*.pyc", "src/__pycache__/", "src/__pycache__/**",
            "docs/_build/", "docs/_build/**"
        ]
        mock_make_patterns.return_value = expected_patterns
        
        # Update Claude Code's ignorePatterns
        updated, errors = update_claude_ignore_patterns(mock_git_repo, dry_run=False, verbosity=0)
        
        # Should have updated 1 directory with no errors
        assert updated == 1
        assert errors == 0
        
        # Check that subprocess.run was called to set ignorePatterns
        assert mock_subprocess.call_count >= 1
        
        # Find the call that set ignorePatterns
        set_call = None
        for call in mock_subprocess.call_args_list:
            args = call[0][0]
            if len(args) >= 3 and args[1] == "config" and args[2] == "set":
                set_call = call
                break
        
        assert set_call is not None
        
        # Check the patterns that were set
        patterns_json = set_call[0][0][4]
        patterns = json.loads(patterns_json)
        
        # Should match our expected patterns
        assert patterns == expected_patterns
    
    @patch("subprocess.run")
    def test_scan_update_status(self, mock_subprocess, mock_git_repo, setup_mock_config):
        """Test scanning, updating, and checking status."""
        # Configure subprocess mock to return empty patterns initially
        mock_subprocess.return_value.stdout = "[]"
        mock_subprocess.return_value.returncode = 0
        
        # First, scan the repository
        scan_gitignore_files(mock_git_repo, verbosity=0)
        
        # Then, update Claude Code's ignorePatterns
        updated, errors = update_claude_ignore_patterns(mock_git_repo, dry_run=False, verbosity=0)
        
        # Change the mock to return our patterns for status check
        expected_patterns = [
            "*.log", "node_modules/", "node_modules/**",
            "src/*.pyc", "src/__pycache__/", "src/__pycache__/**",
            "docs/_build/", "docs/_build/**"
        ]
        mock_subprocess.return_value.stdout = json.dumps(expected_patterns)
        
        # Check the status
        synced, unsynced = report_status(mock_git_repo, verbosity=0)
        
        # Should report 1 synced directory and 0 unsynced
        assert synced == 1
        assert unsynced == 0
    
    @patch("subprocess.run")
    @patch("builtins.input", return_value="y")
    @patch("updater.is_patterns_different")
    @patch("updater.find_changed_gitignores")
    @patch("updater.make_cc_patterns")  # This is the correct module path
    def test_full_workflow_with_reset(self, mock_make_patterns, mock_find_changed, mock_is_diff, mock_input, mock_subprocess, mock_git_repo, setup_mock_config):
        """Test the full workflow including resetting."""
        # Configure subprocess mock to return empty patterns initially
        mock_subprocess.return_value.stdout = "[]"
        mock_subprocess.return_value.returncode = 0
        
        # Setup config with gitignore files
        root_gitignore = os.path.join(mock_git_repo, ".gitignore")
        src_gitignore = os.path.join(mock_git_repo, "src", ".gitignore")
        docs_gitignore = os.path.join(mock_git_repo, "docs", ".gitignore")
        
        # Add files to the file_index
        setup_mock_config["file_index"] = {
            mock_git_repo: {
                root_gitignore: "outdated_hash1",
                src_gitignore: "outdated_hash2",
                docs_gitignore: "outdated_hash3"
            }
        }
        
        # Mock find_changed_gitignores to return our mock_git_repo
        # This simulates that the directory has changed .gitignore files
        mock_find_changed.return_value = {mock_git_repo}
        
        # Force is_patterns_different to return True to trigger an update
        mock_is_diff.return_value = True
        
        # Mock the pattern generation to return known patterns
        expected_patterns = [
            "*.log", "node_modules/", "node_modules/**",
            "src/*.pyc", "src/__pycache__/", "src/__pycache__/**",
            "docs/_build/", "docs/_build/**"
        ]
        mock_make_patterns.return_value = expected_patterns
        
        # 1. Update Claude Code's ignorePatterns
        updated, errors = update_claude_ignore_patterns(mock_git_repo, dry_run=False, verbosity=0)
        
        # Should have updated 1 directory
        assert updated == 1
        
        # Make sure our directory is in ever_touched
        setup_mock_config["ever_touched"] = [mock_git_repo]
        
        # 3. Reset the patterns
        reset_count, reset_errors = reset_claude_ignore_patterns(interactive=False, dry_run=False, verbosity=0)
        
        # Should have reset 1 directory
        assert reset_count == 1
        assert reset_errors == 0
        
        # Check that the last subprocess call was to set empty patterns
        last_call = mock_subprocess.call_args_list[-1]
        args = last_call[0][0]
        
        assert args[0] == "claude"
        assert args[1] == "config"
        assert args[2] == "set"
        assert args[3] == "ignorePatterns"
        assert args[4] == "[]"  # Empty patterns