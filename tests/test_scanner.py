#!/usr/bin/env python3

import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Import module to test
from scanner import (
    compute_file_hash,
    find_gitignore_files,
    organize_gitignore_files,
    scan_gitignore_files
)

class TestScannerFunctions:
    """Test scanner functions."""
    
    def test_compute_file_hash(self, mock_git_repo):
        """Test computing file hash."""
        # Test with root .gitignore
        gitignore_path = os.path.join(mock_git_repo, ".gitignore")
        hash1 = compute_file_hash(gitignore_path)
        
        # Hash should be a 32-character md5 hexadecimal string
        assert len(hash1) == 32
        assert all(c in "0123456789abcdef" for c in hash1)
        
        # Test with a different file
        src_gitignore_path = os.path.join(mock_git_repo, "src", ".gitignore")
        hash2 = compute_file_hash(src_gitignore_path)
        
        # Should be a different hash
        assert hash1 != hash2
    
    def test_find_gitignore_files(self, mock_git_repo):
        """Test finding .gitignore files."""
        gitignore_files = find_gitignore_files(mock_git_repo)
        
        # Should find 3 .gitignore files
        assert len(gitignore_files) == 3
        
        # Check that they're the correct ones
        root_gitignore = os.path.join(mock_git_repo, ".gitignore")
        src_gitignore = os.path.join(mock_git_repo, "src", ".gitignore")
        docs_gitignore = os.path.join(mock_git_repo, "docs", ".gitignore")
        
        assert root_gitignore in gitignore_files
        assert src_gitignore in gitignore_files
        assert docs_gitignore in gitignore_files
    
    def test_organize_gitignore_files(self, mock_git_repo):
        """Test organizing .gitignore files by top-level git dir."""
        # Find the gitignore files
        gitignore_files = find_gitignore_files(mock_git_repo)
        
        # Organize them
        organized = organize_gitignore_files(gitignore_files)
        
        # Should have one entry for the repo
        assert len(organized) == 1
        assert mock_git_repo in organized
        
        # Should have 3 files in that entry
        assert len(organized[mock_git_repo]) == 3
        
        # Check that the files are correct
        root_gitignore = os.path.join(mock_git_repo, ".gitignore")
        src_gitignore = os.path.join(mock_git_repo, "src", ".gitignore")
        docs_gitignore = os.path.join(mock_git_repo, "docs", ".gitignore")
        
        assert root_gitignore in organized[mock_git_repo]
        assert src_gitignore in organized[mock_git_repo]
        assert docs_gitignore in organized[mock_git_repo]
        
        # Check that the hashes are correct format
        for hash_value in organized[mock_git_repo].values():
            assert len(hash_value) == 32
            assert all(c in "0123456789abcdef" for c in hash_value)
    
    @patch("scanner.save_config")
    def test_scan_gitignore_files(self, mock_save_config, mock_git_repo, setup_mock_config):
        """Test scanning .gitignore files and updating config."""
        # Scan the gitignore files
        top_level_count, gitignore_count = scan_gitignore_files(mock_git_repo, verbosity=0)
        
        # Should find 1 top-level dir and 3 gitignore files
        assert top_level_count == 1
        assert gitignore_count == 3
        
        # Check that save_config was called
        mock_save_config.assert_called_once()
        
        # Get the config that was saved
        config = mock_save_config.call_args[0][0]
        
        # Check that the file_index was updated
        assert mock_git_repo in config["file_index"]
        assert len(config["file_index"][mock_git_repo]) == 3
        
        # Check that the files are correct
        root_gitignore = os.path.join(mock_git_repo, ".gitignore")
        src_gitignore = os.path.join(mock_git_repo, "src", ".gitignore")
        docs_gitignore = os.path.join(mock_git_repo, "docs", ".gitignore")
        
        assert root_gitignore in config["file_index"][mock_git_repo]
        assert src_gitignore in config["file_index"][mock_git_repo]
        assert docs_gitignore in config["file_index"][mock_git_repo]