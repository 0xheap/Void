# Post-Install Scripts Feature

## Overview
Added support for running custom shell commands automatically after app installation.

## Implementation

### Changes Made

1. **installer.py** - Added `run_post_install_scripts()` function
   - Executes shell commands in sequence
   - Supports placeholder replacement: `{bin}` and `{link}`
   - 5-minute timeout per command
   - Graceful error handling (failures don't stop installation)

2. **apps.py** - Added example to vscode
   ```python
   "post_install": [
       "{link} --install-extension ms-python.python",
       "{link} --install-extension dbaeumer.vscode-eslint"
   ]
   ```

3. **README.md** - Complete documentation
   - Added to "Optional Fields" section
   - New Example 5 showing VSCode with extensions
   - Troubleshooting section for script failures

4. **tests/test_post_install.py** - Unit tests
   - Placeholder replacement verification
   - Success/failure handling
   - All tests passing ✓

## Usage

### In App Definition
```json
{
    "myapp": {
        "name": "My App",
        "url": "https://example.com/app.tar.gz",
        "type": "tar.gz",
        "bin_path": "app/bin/app",
        "link_name": "myapp",
        "post_install": [
            "{link} --version",
            "{bin} --setup",
            "echo 'Installation complete!'"
        ]
    }
}
```

### Placeholders
- `{bin}` → Full path to installed binary (e.g., `/goinfre/user/void/apps/vscode/VSCode-linux-x64/bin/code`)
- `{link}` → Full path to symlink (e.g., `/home/user/bin/code`)

### Example Output
```
--- Running post-install scripts for vscode ---
[1/2] Executing: /home/user/bin/code --install-extension ms-python.python
  ✓ Success
  Output: Extension 'ms-python.python' v2024.0.0 was successfully installed.
[2/2] Executing: /home/user/bin/code --install-extension dbaeumer.vscode-eslint
  ✓ Success
  Output: Extension 'dbaeumer.vscode-eslint' v2.4.4 was successfully installed.
```

## Use Cases

1. **IDE Extensions** - Auto-install VSCode/JetBrains plugins
2. **Configuration** - Set default preferences
3. **Dependencies** - Download additional resources
4. **Verification** - Run `--version` to confirm installation
5. **Notifications** - Echo completion messages

## Features

- ✅ Sequential execution (order matters)
- ✅ Timeout protection (5 min per command)
- ✅ Error handling (non-blocking)
- ✅ Output capture (stdout/stderr)
- ✅ Shell support (pipes, redirects work)
- ✅ Placeholder substitution

## Testing

Run tests:
```bash
python3 tests/test_post_install.py
```

All 3 tests passing:
- ✓ Placeholder replacement
- ✓ Success handling
- ✓ Failure handling

## Notes

- Scripts run AFTER binary linking and data path setup
- Failures are logged but don't stop installation
- Scripts have access to the installed binary via `{link}`
- Use non-interactive flags (e.g., `-y`, `--yes`) to avoid hangs
