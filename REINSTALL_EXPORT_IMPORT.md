# Reinstall, Export & Import Features

## Overview
Three new commands for managing app installations across workstations.

---

## 1. Reinstall

Quickly reinstall an app (uninstall + install in one command).

### Usage
```bash
./void.py reinstall <app_name>
```

### Example
```bash
$ ./void.py reinstall vscode

============================================================
 Reinstalling vscode
============================================================

Uninstalling vscode...
--- Uninstalling vscode ---
Removing symlink: /home/user/bin/code
Removing desktop entry: /home/user/.local/share/applications/void_vscode.desktop
Removing app directory: /goinfre/user/void/apps/vscode
Successfully uninstalled vscode

Installing vscode...
--- Installing vscode ---
Downloading...
[████████████████████] 100%
Extracting...
Creating symlink...
Successfully installed vscode!
```

### Use Cases
- **Fix broken installation** - App not working? Reinstall it
- **Update app** - After checking for updates
- **Reset configuration** - Start fresh with clean install
- **Repair corrupted files** - Reinstall fixes file issues

---

## 2. Export

Export list of installed apps to JSON format.

### Usage
```bash
./void.py export > my-setup.json
```

### Example
```bash
$ ./void.py export

{
  "version": "1.0",
  "exported_at": "2026-02-08T20:55:00.000000+00:00",
  "apps": [
    "vscode",
    "discord",
    "telegram",
    "neovim",
    "sublime"
  ]
}
```

### Output Format
- **version**: Export format version
- **exported_at**: ISO timestamp
- **apps**: Array of installed app names

### Use Cases
- **Backup** - Save your app list before major changes
- **Documentation** - Record what's installed
- **Migration** - Move to new workstation
- **Sharing** - Share your setup with others

---

## 3. Import

Install apps from exported JSON file.

### Usage
```bash
./void.py import <file.json>
./void.py import <file.json> -y  # Skip confirmation
```

### Example
```bash
$ ./void.py import my-setup.json

============================================================
 Importing 5 apps
============================================================

  • vscode
  • discord
  • telegram
  • neovim
  • sublime

Install these apps? (yes/no): yes

Installing vscode...
--- Installing vscode ---
Successfully installed vscode!

Installing discord...
--- Installing discord ---
Successfully installed discord!

Installing telegram...
--- Installing telegram ---
Successfully installed telegram!

Installing neovim...
--- Installing neovim ---
Successfully installed neovim!

Installing sublime...
--- Installing sublime ---
Successfully installed sublime!

============================================================
Import complete: 5 installed, 0 failed
============================================================
```

### With -y Flag (Skip Confirmation)
```bash
$ ./void.py import my-setup.json -y

============================================================
 Importing 5 apps
============================================================

  • vscode
  • discord
  • telegram
  • neovim
  • sublime

Installing vscode...
...
```

### Error Handling
```bash
$ ./void.py import my-setup.json

============================================================
 Importing 3 apps
============================================================

  • vscode
  • unknown-app
  • discord

Install these apps? (yes/no): yes

Installing vscode...
Successfully installed vscode!

✗ unknown-app: Unknown app

Installing discord...
Successfully installed discord!

============================================================
Import complete: 2 installed, 1 failed
Failed: unknown-app
============================================================
```

---

## Complete Workflow

### Scenario: Moving to New Workstation

**On old workstation:**
```bash
# Export your setup
./void.py export > ~/my-void-setup.json

# Copy file to new workstation (USB, cloud, etc.)
```

**On new workstation:**
```bash
# Clone Void
git clone https://github.com/your-username/void.git
cd void

# Import your setup
./void.py import ~/my-void-setup.json -y

# All your apps are now installed!
```

### Scenario: Backup Before Major Changes

```bash
# Before making changes
./void.py export > backup-$(date +%Y%m%d).json

# Make changes...
./void.py uninstall vscode
./void.py install vscodium

# If something goes wrong, restore
./void.py import backup-20260208.json
```

### Scenario: Share Setup with Team

```bash
# Create team setup
./void.py export > team-setup.json

# Share with team
# Team members can install same apps:
./void.py import team-setup.json
```

### Scenario: Fix Broken App

```bash
# App not working?
./void.py reinstall vscode

# Fresh install, should work now
```

---

## Implementation Details

### Reinstall
- Calls `uninstall_app()` if app is installed
- Then calls `install_app()`
- Single command for convenience

### Export
- Gets list of installed apps via `get_installed_apps()`
- Creates JSON with version, timestamp, app names
- Outputs to stdout (redirect to file)

### Import
- Reads JSON file
- Validates format
- Shows list of apps to install
- Asks for confirmation (unless -y)
- Installs each app sequentially
- Reports success/failure counts

---

## File Format

### Export JSON Structure
```json
{
  "version": "1.0",
  "exported_at": "2026-02-08T20:55:00.000000+00:00",
  "apps": [
    "app1",
    "app2",
    "app3"
  ]
}
```

### Fields
- **version** (string): Format version for compatibility
- **exported_at** (string): ISO 8601 timestamp
- **apps** (array): List of app names (strings)

### Compatibility
- Only app names are stored (not versions or URLs)
- Apps are installed using current definitions in `apps.py`
- Unknown apps are skipped with error message

---

## Tips

### Export
```bash
# Export to file
./void.py export > my-setup.json

# Export with timestamp
./void.py export > setup-$(date +%Y%m%d-%H%M%S).json

# View without saving
./void.py export | less
```

### Import
```bash
# Preview before importing
cat my-setup.json

# Import with confirmation
./void.py import my-setup.json

# Import without confirmation
./void.py import my-setup.json -y

# Import from URL (if downloaded)
curl https://example.com/setup.json | ./void.py import /dev/stdin -y
```

### Reinstall
```bash
# Reinstall single app
./void.py reinstall vscode

# Reinstall multiple (loop)
for app in vscode discord telegram; do
  ./void.py reinstall $app
done
```

---

## Benefits

1. **Migration** - Easy move between workstations
2. **Backup** - Save your setup before changes
3. **Recovery** - Restore after issues
4. **Sharing** - Share setups with team
5. **Automation** - Script installations
6. **Quick Fix** - Reinstall broken apps

---

## Future Enhancements

- Export with versions (pin specific versions)
- Import from URL directly
- Selective import (choose which apps)
- Batch reinstall (reinstall all)
- Export with custom apps config
- Import validation (check before installing)
