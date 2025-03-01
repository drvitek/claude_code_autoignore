# Claude Code Autoignore (cc_autoignore)

A tool for synchronizing Claude Code's ignore configuration with `.gitignore` patterns.  A `.gitignore` entry like:
```
node_modules/
```

should be converted to Claude Code's `ignorePatterns` configuration format as
```
claude config set ignorePatterns '["node_modules/", "node_modules/**"]'
```

This tool automates this conversion.  More specifically, it can:
1. Find all `.gitignore` files in a target directory (including handling nested `.gitignore` files).
2. Convert `.gitignore` patterns to Claude Code's `ignorePatterns` format
3. Automatically run the appropriate `claude config set ignorePatterns` commands
4. Track `.gitignore` changes to efficiently update only when needed
5. Apply global defaults to handle desired differences between Git ignore behavior and Claude Code ignore behavior.

## WARNINGS

- Negation patterns (lines starting with `!`) are currently **COMPLETELY SKIPPED.**
- I'm not necessarily a careful programmer, I built this with Claude Code, and Claude Code is rapidly changing.  **USE AT YOUR OWN RISK.**

In particular, this code will probably do only the following things to your system:
- read files
- call lots of `claude config get`/`set` commands
- write some JSON data to `~/.cc_autoignore_config`
    - change this location via `CONFIG_FILEPATH` in `cc_autoignore.py`

If you have really complicated `.gitignore` files, it's conceivable that this tool could break your Claude Code setup and require a reinstall.  Sorry!

## features

- **Scan**: Recursively find all `.gitignore` files in your directory
- **Update**: Sync changed `.gitignore` files with Claude Code's config. Avoids unnecessary updates with file hash tracking.
- **Status**: View which `.gitignore` files are tracked and their status
- **Reset**: Clear all Claude Code ignore patterns set by the tool
- **Dry Run**: Preview changes without applying them
- **Default Config**: Set global defaults for the tool

## setup

1. Put `cc_autoignore` in `/usr/local/bin/` or wherever.
2. Modify `cc_autoignore` to point to wherever you've put `cc_autoignore.py`
   - default `/usr/local/bin/py_src/`.

(this is stupid and will probably change in the future!)

## config

There are currently four global config settings:
- `verbosity`: how verbose to be by default, integer 0-4 (inclusive).
- `always_add`: lines to always add to `ignorePatterns` configuration.
- `always_remove`: lines in `.gitignore` files to always remove when building `ignorePatterns` configuration.

## usage


```bash
# Scan a directory for .gitignore files
cc_autoignore scan --target=/path/to/directory

# View status of tracked .gitignore files vs. Claude Code configurations
cc_autoignore status

# Update Claude Code ignore patterns (dry run)
cc_autoignore update --dry-run

# Update Claude Code ignore patterns
cc_autoignore update

# Reset all Claude Code ignore patterns set by the tool
cc_autoignore reset
```

## the future??

- Support for negation patterns would be nice.
- Better pattern conversion; I'm sure there are weird edge cases this tool currently messes up.
- Global `.gitignore` handling.
- I have no idea how Macs (or Claude Code on WSL) work and if anything here will break.
- Git hooks for automatic updates on `.gitignore` changes.

PRs welcome!  Email me (code @ domain on my profile) if you're interested in becoming a maintainer.

## License

[MIT License](LICENSE)
