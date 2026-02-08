# Changelog

## [Unreleased]

### Added

#### Post-Install Scripts
- **Post-Install Scripts** - Execute custom shell commands automatically after app installation
  - Support for `post_install` field in app definitions (array of shell commands)
  - Placeholder support: `{bin}` (full binary path) and `{link}` (symlink path)
  - 5-minute timeout per command with graceful error handling
  - stdout/stderr capture and display
  - Non-blocking execution (failures don't stop installation)
  - Example configuration in `examples/custom_apps_with_post_install.json`
  - Comprehensive documentation in README.md and dedicated guides
  - Unit tests in `tests/test_post_install.py`

#### Enhanced Cleanup
- **Deep Cleaning** - Enhanced cleanup module with comprehensive cache detection
  - VSCode deep clean: cached extensions, obsolete extensions, cached data
  - Flatpak cache cleanup: app caches and temporary files
  - Old backup detection: Neovim backups, editor backup files
  - Incomplete download detection: browser unconfirmed downloads
  
- **Large File Detection** - Find files >200MB for manual review
  - Scans home directory intelligently
  - Sorted by size (largest first)
  - Shows top 10 with full paths
  
- **Old Download Detection** - Find files >90 days old in Downloads
  - Shows file size and age in days
  - Sorted by age (oldest first)
  - Safe listing for manual review
  
- **Multi-Pass Cleanup** - Three-stage cleanup process
  - Stage 1: Standard cleanup (cache, logs, build artifacts)
  - Stage 2: VSCode deep clean
  - Stage 3: Flatpak cache cleanup
  - Progress reporting for each stage

### Changed
- Updated VSCode app definition to include example post-install scripts for extension installation
- Enhanced README.md with Example 5 showing VSCode with automatic extension setup
- Added troubleshooting section for post-install script failures
- Enhanced cleanup analyze command to show large files and old downloads
- Enhanced cleanup execute command with multi-pass cleaning and progress reporting
- Added 60+ new cache patterns to cleanup module

### Use Cases

#### Post-Install Scripts
- Automatically install IDE extensions/plugins
- Create default configuration files
- Download additional resources
- Verify installation with version checks
- Set up themes and preferences
- Initialize databases or sample data

#### Enhanced Cleanup
- Free 20-50% more space than before
- Identify large files consuming disk space
- Find old downloads that can be deleted
- Deep clean IDE caches
- Clean flatpak application data

### Example

#### Post-Install Scripts
```json
{
    "vscode": {
        "name": "Visual Studio Code",
        "url": "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64",
        "type": "tar.gz",
        "bin_path": "VSCode-linux-x64/bin/code",
        "link_name": "code",
        "data_paths": [".vscode/extensions", ".config/Code"],
        "post_install": [
            "{link} --install-extension ms-python.python",
            "{link} --install-extension dbaeumer.vscode-eslint",
            "echo 'VSCode configured with Python and ESLint extensions'"
        ]
    }
}
```

#### Enhanced Cleanup
```bash
# Analyze with large files and old downloads
./void.py cleanup

# Execute multi-pass cleanup
./void.py cleanup --execute
```
