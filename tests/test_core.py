#!/usr/bin/env python3

import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Import modules to test
from core import (
    get_config,
    save_config,
    find_top_level_gitdir,
    get_gitignore_patterns,
    convert_pattern_to_cc_format,
    make_cc_patterns,
    get_cc_patterns,
    set_cc_patterns
)

class TestConfigFunctions:
    """Test configuration-related functions."""
    
    def test_get_config_new(self, temp_config_file):
        """Test get_config with a new config file."""
        # Ensure the file doesn't exist yet
        assert not os.path.exists(temp_config_file)
        
        # Get the config, which should create a default one
        config = get_config()
        
        # Check that the file was created
        assert os.path.exists(temp_config_file)
        
        # Check that it has the expected structure
        assert "file_index" in config
        assert "ever_touched" in config
        assert "options" in config
        assert "verbosity" in config["options"]
        assert "always_add" in config["options"]
        assert "always_remove" in config["options"]
    
    def test_get_config_existing(self, setup_mock_config):
        """Test get_config with an existing config file."""
        # Get the config, which should read our mock one
        config = get_config()
        
        # Check that it matches the mock config
        assert config == setup_mock_config
    
    def test_save_config(self, temp_config_file):
        """Test save_config function."""
        # Create a test config
        test_config = {
            "file_index": {"test": {"path": "hash"}},
            "ever_touched": ["/test/path"],
            "options": {
                "verbosity": 2,
                "always_add": ["pattern1"],
                "always_remove": ["pattern2"]
            }
        }
        
        # Save it
        save_config(test_config)
        
        # Read it back
        with open(temp_config_file, 'r') as f:
            loaded_config = json.load(f)
        
        # Check that it matches
        assert loaded_config == test_config

class TestGitFunctions:
    """Test git-related functions."""
    
    def test_find_top_level_gitdir(self, mock_git_repo):
        """Test finding the top-level git directory."""
        # Test from the repo root
        assert find_top_level_gitdir(mock_git_repo) == mock_git_repo
        
        # Test from a subdirectory
        src_dir = os.path.join(mock_git_repo, "src")
        assert find_top_level_gitdir(src_dir) == mock_git_repo
        
        # Test from a non-git directory
        non_git_dir = os.path.join(os.path.dirname(mock_git_repo), "non_git")
        os.makedirs(non_git_dir, exist_ok=True)
        assert find_top_level_gitdir(non_git_dir) is None
    
    def test_get_gitignore_patterns(self, mock_git_repo):
        """Test parsing .gitignore patterns."""
        # Test the root .gitignore
        root_gitignore = os.path.join(mock_git_repo, ".gitignore")
        patterns = get_gitignore_patterns(root_gitignore)
        
        # Should have 2 patterns, skipping the comment
        assert len(patterns) == 2
        assert "*.log" in patterns
        assert "node_modules/" in patterns
        
        # Test a nested .gitignore
        src_gitignore = os.path.join(mock_git_repo, "src", ".gitignore")
        patterns = get_gitignore_patterns(src_gitignore)
        
        # Should have 2 patterns, skipping the comment
        assert len(patterns) == 2
        assert "*.pyc" in patterns
        assert "__pycache__/" in patterns

class TestPatternFunctions:
    """Test pattern conversion and processing functions."""
    
    def test_convert_pattern_to_cc_format(self):
        """Test converting .gitignore patterns to Claude Code format."""
        # Test directory pattern
        dir_patterns = convert_pattern_to_cc_format("node_modules/")
        assert len(dir_patterns) == 2
        assert "node_modules/" in dir_patterns
        assert "node_modules/**" in dir_patterns
        
        # Test file pattern
        file_patterns = convert_pattern_to_cc_format("*.log")
        assert len(file_patterns) == 1
        assert "*.log" in file_patterns
        
        # Test pattern with leading slash
        slash_patterns = convert_pattern_to_cc_format("/build")
        assert len(slash_patterns) == 1
        assert "build" in slash_patterns
    
    def test_make_cc_patterns(self, setup_mock_config, mock_git_repo):
        """Test creating combined ignorePatterns."""
        config = setup_mock_config
        
        # Create a file_index entry for our mock repo
        root_gitignore = os.path.join(mock_git_repo, ".gitignore")
        src_gitignore = os.path.join(mock_git_repo, "src", ".gitignore")
        docs_gitignore = os.path.join(mock_git_repo, "docs", ".gitignore")
        
        config["file_index"] = {
            mock_git_repo: {
                root_gitignore: "hash1",
                src_gitignore: "hash2",
                docs_gitignore: "hash3"
            }
        }
        
        # Generate patterns
        patterns = make_cc_patterns(config, mock_git_repo)
        
        # Should include patterns from all three .gitignore files
        # With proper prefixes for nested files
        assert "*.log" in patterns
        assert "node_modules/" in patterns
        assert "node_modules/**" in patterns
        assert "src/*.pyc" in patterns
        assert "src/__pycache__/" in patterns
        assert "src/__pycache__/**" in patterns
        assert "docs/_build/" in patterns
        assert "docs/_build/**" in patterns

class TestClaudeCodeFunctions:
    """Test functions that interact with Claude Code CLI."""
    
    def test_get_cc_patterns(self, mock_subprocess_run):
        """Test getting ignorePatterns from Claude Code."""
        # Configure mock to return specific patterns
        mock_subprocess_run.return_value.stdout = '["*.log", "node_modules/", "node_modules/**"]'
        
        # Get patterns
        patterns = get_cc_patterns("/test/dir")
        
        # Check that subprocess.run was called correctly
        mock_subprocess_run.assert_called_once()
        args, kwargs = mock_subprocess_run.call_args
        assert args[0] == ["claude", "config", "get", "ignorePatterns"]
        assert kwargs["cwd"] == "/test/dir"
        
        # Check the returned patterns
        assert len(patterns) == 3
        assert "*.log" in patterns
        assert "node_modules/" in patterns
        assert "node_modules/**" in patterns
    
    def test_set_cc_patterns(self, mock_subprocess_run):
        """Test setting ignorePatterns in Claude Code."""
        # Set patterns
        test_patterns = ["*.log", "node_modules/", "node_modules/**"]
        success = set_cc_patterns("/test/dir", test_patterns)
        
        # Check that subprocess.run was called correctly
        mock_subprocess_run.assert_called_once()
        args, kwargs = mock_subprocess_run.call_args
        assert args[0] == ["claude", "config", "set", "ignorePatterns", json.dumps(test_patterns)]
        assert kwargs["cwd"] == "/test/dir"
        
        # Check the result
        assert success is True
    
    def test_set_cc_patterns_dry_run(self, mock_subprocess_run):
        """Test setting ignorePatterns in dry run mode."""
        # Set patterns in dry run mode
        test_patterns = ["*.log", "node_modules/", "node_modules/**"]
        success = set_cc_patterns("/test/dir", test_patterns, dry_run=True)
        
        # Check that subprocess.run was not called
        mock_subprocess_run.assert_not_called()
        
        # Check the result
        assert success is True