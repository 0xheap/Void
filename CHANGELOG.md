# Changelog

## [Unreleased]

### Added
- **Post-Install Scripts** - Execute custom shell commands automatically after app installation
  - Support for `post_install` field in app definitions (array of shell commands)
  - Placeholder support: `{bin}` (full binary path) and `{link}` (symlink path)
  - 5-minute timeout per command with graceful error handling
  - stdout/stderr capture and display
  - Non-blocking execution (failures don't stop installation)
  - Example configuration in `examples/custom_apps_with_post_install.json`
  - Comprehensive documentation in README.md and dedicated guides
  - Unit tests in `tests/test_post_install.py`

### Changed
- Updated VSCode app definition to include example post-install scripts for extension installation
- Enhanced README.md with Example 5 showing VSCode with automatic extension setup
- Added troubleshooting section for post-install script failures

### Use Cases
- Automatically install IDE extensions/plugins
- Create default configuration files
- Download additional resources
- Verify installation with version checks
- Set up themes and preferences
- Initialize databases or sample data

### Example
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
