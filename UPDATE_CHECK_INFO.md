# Update Check & App Info Features

## Overview
Added two new commands to manage and inspect installed applications.

## Features Added

### 1. Check Updates (`./void.py check-updates`)

Checks all installed apps for available updates by comparing metadata (ETag, Last-Modified, Content-Length).

**Usage:**
```bash
./void.py check-updates
```

**Output:**
```
============================================================
 Checking for Updates
============================================================

Checking Visual Studio Code... ✓ Update available (ETag changed)
Checking Discord... ✓ Up to date
Checking Telegram... ✗ No metadata found

============================================================
Summary: 1 updates, 1 up-to-date, 1 errors

Updates available:
  • Visual Studio Code (vscode)

Run './void.py install <app_name>' to update
```

**How it works:**
- Fetches remote metadata (ETag, Last-Modified, Content-Length)
- Compares with installed app metadata
- Reports changes that indicate updates

### 2. App Info (`./void.py info <app_name>`)

Shows detailed information about an installed or available app.

**Usage:**
```bash
./void.py info vscode
```

**Output (Not Installed):**
```
============================================================
 App Information: vscode
============================================================

Status: Not installed
Name: Visual Studio Code
URL: https://code.visualstudio.com/sha/download?build=stable&os=linux-x64
Type: tar.gz
```

**Output (Installed):**
```
============================================================
 App Information: vscode
============================================================

Name: Visual Studio Code
Status: Installed
Size: 350.25 MB
Install Directory: /goinfre/user/void/apps/vscode
Binary: /goinfre/user/void/apps/vscode/VSCode-linux-x64/bin/code
  Exists: ✓
Symlink: /home/user/bin/code
  Exists: ✓
Installed: 2026-02-08 15:30:45
Type: tar.gz
Source URL: https://code.visualstudio.com/sha/download?build=stable&os=linux-x64

Data Paths:
  • .vscode/extensions: ✓ symlinked
  • .config/Code: ✓ symlinked

Checking for updates... ✓ Up to date
```

**Information Shown:**
- Installation status
- Size on disk
- Install directory and binary path
- Symlink status
- Installation date
- Data path status (symlinked or not)
- Update availability

## Implementation

### New Functions in `modules/installer.py`

**`get_installed_apps()`**
- Returns list of all installed apps with metadata
- Calculates size for each app
- Used by check-updates command

**`check_app_update(app_name)`**
- Checks if an app has an update available
- Compares ETag, Last-Modified, Content-Length
- Returns status: update_available, up_to_date, no_metadata, error

**`get_app_info(app_name)`**
- Gets detailed information about an app
- Checks binary, symlink, and data path status
- Works for both installed and non-installed apps

### New Commands in `void.py`

**`cmd_check_updates(args)`**
- Iterates through all installed apps
- Checks each for updates
- Shows summary with counts

**`cmd_info(args)`**
- Shows detailed app information
- Includes update check
- Formatted output with status indicators

## Use Cases

### Check Updates
```bash
# Check all installed apps for updates
./void.py check-updates

# Then update specific app
./void.py install vscode
```

### App Info
```bash
# Check if app is installed and its status
./void.py info vscode

# Verify installation after install
./void.py install discord
./void.py info discord

# Debug broken installation
./void.py info myapp
# Shows if binary/symlink exists
```

## Update Detection

Updates are detected by comparing:

1. **ETag** - HTTP entity tag (most reliable)
2. **Last-Modified** - File modification date
3. **Content-Length** - File size

If any of these change, an update is considered available.

**Note:** Some servers don't provide these headers, resulting in "No metadata" status.

## Examples

### Scenario 1: Check for updates
```bash
$ ./void.py check-updates

Checking Visual Studio Code... ✓ Update available (ETag changed)
Checking Discord... ✓ Up to date
Checking Neovim... ✓ Up to date

Summary: 1 updates, 2 up-to-date, 0 errors

Updates available:
  • Visual Studio Code (vscode)

Run './void.py install vscode' to update
```

### Scenario 2: Get app info before installing
```bash
$ ./void.py info telegram

Status: Not installed
Name: Telegram Desktop
URL: https://telegram.org/dl/desktop/linux
Type: tar.xz
```

### Scenario 3: Verify installation
```bash
$ ./void.py install vscode
# ... installation output ...

$ ./void.py info vscode

Name: Visual Studio Code
Status: Installed
Size: 350.25 MB
Binary: ✓
Symlink: ✓
Data Paths:
  • .vscode/extensions: ✓ symlinked
  • .config/Code: ✓ symlinked

Checking for updates... ✓ Up to date
```

### Scenario 4: Debug broken installation
```bash
$ ./void.py info myapp

Name: My App
Status: Installed
Size: 50.00 MB
Binary: ✗  # <-- Problem!
Symlink: ✗  # <-- Problem!

# Fix with repair
$ ./void.py repair myapp
```

## Benefits

1. **Update Awareness** - Know when apps have updates
2. **Installation Verification** - Confirm apps installed correctly
3. **Debugging** - Identify broken installations
4. **Size Tracking** - See how much space each app uses
5. **Status Overview** - Quick health check for any app

## Files Modified

1. `modules/installer.py`
   - Added `get_installed_apps()` function
   - Added `check_app_update()` function
   - Added `get_app_info()` function

2. `void.py`
   - Added `cmd_check_updates()` command
   - Added `cmd_info()` command
   - Added argument parsers for both commands

## Testing

```bash
# Test syntax
python3 -m py_compile modules/installer.py void.py

# Test commands
./void.py check-updates
./void.py info vscode
./void.py info nonexistent

# All working ✓
```

## Future Enhancements

- Auto-update command (download and install updates)
- Update notifications on startup
- Version comparison (if version info available)
- Batch info command (show info for multiple apps)
- Export app list with versions
