The project is currently high-level described in the README.md file; look there for overall hints.

Configuration details:
 - stored at CONFIG_FILEPATH (this should just be a magic constant in core.py, default ~/.cc_autoignore_config)
 - flat JSON file, probably not big enough to bother compressing
 - top-level fields: file_index, ever_touched, options (described in more detail below)

file_index config field:

This should be a two-level dictionary.  The idea here is that we want to store the location of each top-level .git file, because we *only call `claude config set ignorePatterns` at the top level, not at each lower level.  But we want to store the locations of any lower-level .gitignore files in this data structure so that we can look at them and figure out how to combine all of the patterns into one global pattern, which we'll then pass to `claude code set ignorePatterns`.

More specifically, top-level keys are just filepaths to top-level .gitignore files.  Top-level values are dicts with keys filepaths to lower-level .gitignore files and values MD5 hashes.  Note that we need to include the top-level .gitignore file in this dict!

ever_touched config field:

In order to implement the reset command, we want to keep a list of every directory that we've ever run `claude config set ignorePatterns` in, so that we can reset all of them.  We should update this field only when we do a `cc_autoignore update` or `cc_autoignore` command (unless the update is a dry run).

options config field:
Not quite sure what all the global options should be just yet.  At the very least we should have:
- an int verbosity level (more is higher).
- two lists of strings (always_add, always_remove); these are entries to add/remove from ignorePatterns configuration whenever we call make_cc_patterns.

Top-level commands:
 1. scan: look in a target dir (default ~) and add all .gitignore files to file_index, handling nested .gitignore files appropriately
 2. status: report on all tracked .gitignore files: build intended ignorePatterns and compare with obtained Claude Code config in each top-level directory. 
 3. update: update all Claude Code settings under a given directory (default ~).  so we should look for all top-level keys in file_index that are under target, then prepare the appropriate ignorePatterns settings.
 4. reset: at every dir in ever_touched, set ignorePatterns to [].  probably want an -i flag to allow going through ever_touched line-by-line.  also a global "are you sure" confirmation if no i flag.
 5. config: manage global configuration options (verbosity and add/remove lists).  right now it's probably OK to just accept string-list arguments from CLI; maybe in the future we can implement reading config from files.


Low-level functions:
 - Probably the primary low-level function is make_cc_patterns(config, fp) ("fp" short for filepath).  Here we're assuming fp is a key of file_index dict.  We go through the fps of all .gitignores nested below fp (including fp/.gitignore itself) and create the appropriate ignorePatterns array.  We'll have to be careful about quotation marks!  We then need to modify this per config options.
 - get_cc_pattern(fp) should call `claude config get ignorePatterns` and parse the output to get ignorePatterns.  This will be used to check synchronization status of Claude Code ignore settings.
 - set_cc_pattern(fp, pattern): straightforward setter via calling `claude config set ignorePatterns`.

----

# Future Improvements

Here are potential future improvements to consider:

## Performance Optimizations
- **Pattern Caching**: Cache computed ignorePatterns results for status command
- **Selective Scanning**: Implement more targeted scanning for large repositories
- **Lazy Loading**: Only read .gitignore file contents when needed
- **Parallel Processing**: Use parallel processing for large repositories with many .gitignore files

## Feature Improvements
- **Installation Script**: Create a proper setup.py or improve installation process
- **Issue/PR Templates**: Add GitHub templates for issues and pull requests
- **Documentation Improvements**: Add more detailed docs on configuration, pattern conversion, and usage examples
- **Logging System**: Implement proper logging instead of print statements
- **Global .gitignore Support**: Add support for user's global .gitignore files
- **Negation Pattern Support**: Add support for negation patterns (lines starting with !)
- **Git Hooks Integration**: Create example scripts for git hook integration
- **Better Error Handling**: Add more robust error handling and user-friendly error messages
- **Debug Mode**: Add verbose debug mode to show detailed operations

----

# Project Organization

## File Structure and Responsibilities

The codebase is organized into several modules with specific responsibilities:

### core.py
Contains core functionality and utilities used by other modules.
- **Constants**: CONFIG_FILEPATH
- **Functions**: 
  - get_config() - Load configuration from disk
  - save_config() - Save configuration to disk
  - find_top_level_gitdir() - Find the top-level git directory
  - get_gitignore_patterns() - Parse patterns from .gitignore files
  - convert_pattern_to_cc_format() - Convert .gitignore patterns to Claude Code format
  - make_cc_patterns() - Create combined pattern set for Claude Code
  - get_cc_patterns() - Get current Claude Code ignore patterns
  - is_patterns_different() - Compare pattern sets
  - set_cc_patterns() - Update Claude Code ignore patterns

### scanner.py
Handles scanning for .gitignore files and tracking them.
- **Functions**:
  - compute_file_hash() - Calculate MD5 hash of file contents
  - find_gitignore_files() - Locate all .gitignore files in a directory
  - organize_gitignore_files() - Group .gitignore files by top-level git directory
  - scan_gitignore_files() - Scan and record .gitignore files in config

### updater.py
Manages updating Claude Code settings based on .gitignore files.
- **Functions**:
  - compute_file_hash() - Calculate MD5 hash of file contents
  - find_changed_gitignores() - Find .gitignore files that have changed
  - update_gitignore_hashes() - Update stored hashes for .gitignore files
  - is_patterns_different() - Compare pattern sets
  - update_claude_ignore_patterns() - Update Claude Code ignore patterns

### resetter.py
Handles resetting Claude Code ignore settings.
- **Functions**:
  - reset_claude_ignore_patterns() - Clear all Claude Code ignore patterns

### config_manager.py
Manages configuration settings.
- **Functions**:
  - get_config_value() - Get a specific configuration value
  - set_config_value() - Set a specific configuration value
  - update_config_list() - Add/remove values from list options
  - list_config() - Show all configuration settings
  - reset_config() - Reset configuration to defaults

### status_reporter.py
Reports on synchronization status between .gitignore and Claude Code.
- **Functions**:
  - check_gitignore_exists() - Verify .gitignore file exists
  - get_status_for_directory() - Check sync status for a directory
  - report_status() - Report sync status for all tracked directories

### cc_autoignore.py
Main command-line interface.
- **Functions**:
  - parse_args() - Parse command-line arguments
  - main() - Main entry point

----

I probably haven't documented everything I want super-well.  So feel free to ask me questions and edit this file to clarify things!