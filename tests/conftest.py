#!/usr/bin/env python3

import os
import json
import shutil
import tempfile
import pytest
from typing import Dict, List, Any, Callable
from unittest.mock import patch, MagicMock

# Add parent directory to sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules from the package
import core

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_config_file(temp_dir):
    """Create a temporary config file."""
    config_path = os.path.join(temp_dir, "test_config.json")
    
    # Patch CONFIG_FILEPATH to use our temporary file
    with patch('core.CONFIG_FILEPATH', config_path):
        yield config_path

@pytest.fixture
def mock_config():
    """Return a sample configuration for testing."""
    return {
        "file_index": {},
        "ever_touched": [],
        "options": {
            "verbosity": 1,
            "always_add": [],
            "always_remove": []
        }
    }

@pytest.fixture
def setup_mock_config(temp_config_file, mock_config):
    """Setup a mock configuration file with test data."""
    with open(temp_config_file, 'w') as f:
        json.dump(mock_config, f)
    
    # Patch CONFIG_FILEPATH to use our temporary file
    with patch('core.CONFIG_FILEPATH', temp_config_file):
        yield mock_config

@pytest.fixture
def mock_git_repo(temp_dir):
    """
    Create a mock git repository structure with .gitignore files.
    
    Structure:
    /repo/
      .git/
      .gitignore
      /src/
        .gitignore
      /docs/
        .gitignore
    """
    repo_dir = os.path.join(temp_dir, "repo")
    os.makedirs(repo_dir)
    
    # Create .git directory to mark as a git repo
    os.makedirs(os.path.join(repo_dir, ".git"))
    
    # Create root .gitignore
    with open(os.path.join(repo_dir, ".gitignore"), 'w') as f:
        f.write("# Root .gitignore\n")
        f.write("*.log\n")
        f.write("node_modules/\n")
    
    # Create src directory with .gitignore
    src_dir = os.path.join(repo_dir, "src")
    os.makedirs(src_dir)
    with open(os.path.join(src_dir, ".gitignore"), 'w') as f:
        f.write("# Src .gitignore\n")
        f.write("*.pyc\n")
        f.write("__pycache__/\n")
    
    # Create docs directory with .gitignore
    docs_dir = os.path.join(repo_dir, "docs")
    os.makedirs(docs_dir)
    with open(os.path.join(docs_dir, ".gitignore"), 'w') as f:
        f.write("# Docs .gitignore\n")
        f.write("_build/\n")
    
    return repo_dir

@pytest.fixture
def mock_subprocess_run():
    """Mock the subprocess.run function to simulate Claude Code CLI."""
    with patch('subprocess.run') as mock_run:
        # Configure mock to return empty ignorePatterns by default
        mock_run.return_value.stdout = "[]"
        mock_run.return_value.returncode = 0
        yield mock_run