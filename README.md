# Claude Code Autoignore

A utility for synchronizing Claude Code's ignore configuration with `.gitignore` patterns.

## Overview

Claude Code is a CLI-based LLM-powered coding assistant that operates within Git repositories on local machines. While it has built-in ignore functionality via the `claude config set ignorePatterns` command, it doesn't automatically read or respect existing `.gitignore` files. 

This tool might help you out by:
1. Finding all `.gitignore` files in the target directory
2. Converting Git ignore patterns to Claude Code's ignore format
3. Running the appropriate `claude config set ignorePatterns` commands
4. Tracking `.gitignore` changes to efficiently update only when needed

For example, a `.gitignore` entry like:
```
node_modules/
```

should be converted to Claude Code's format as
```
claude config set ignorePatterns '["node_modules/", "node_modules/**"]'
```

This tool automates that process, handling the conversion and ensuring your Claude Code configuration stays in sync with your Git ignores.

## Features

- **Scan**: Recursively find all `.gitignore` files in your directory
- **Update**: Sync changed `.gitignore` files with Claude Code's config. Avoids unnecessary updates with file hash tracking.
- **Status**: View which `.gitignore` files are tracked and their status
- **Reset**: Clear all Claude Code ignore patterns set by the tool
- **Dry Run**: Preview changes without applying them
- **Default Config**: Set global defaults for the tool

## Current Limitations

- Negation patterns (lines starting with `!`) are currently skipped
- Complex pattern translations may require manual review

### Nested `.gitignore` Files

Git allows `.gitignore` files in subdirectories, with patterns relative to their location. This tool:
- Respects the hierarchical nature of `.gitignore` files
- Runs `claude config set ignorePatterns` commands in the appropriate directories
- Maintains the proper scope of patterns relative to their location

## Usage Examples

```bash
# Scan a directory for .gitignore files
cc_autoignore scan --target=/path/to/directory

# View status of tracked .gitignore files
cc_autoignore status

# Update Claude Code ignore patterns (dry run)
cc_autoignore update --dry-run

# Update Claude Code ignore patterns
cc_autoignore update

# Reset all Claude Code ignore patterns set by the tool
cc_autoignore reset
```

## Future Extensions

Potential future enhancements include:
- Support for negation patterns
- Git hooks for automatic updates on `.gitignore` changes
- More advanced pattern conversion options
- Integration with global Git ignores

PRs welcome!

## Requirements

- Python 3.6+
- Claude Code CLI installed and configured
- Git repository with `.gitignore` files

## License

[MIT License](LICENSE)
