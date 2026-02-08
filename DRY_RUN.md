# Dry Run Mode

## Overview
Preview what an installation would do without actually making any changes.

## Usage

```bash
./void.py install <app_name> --dry-run
```

## What It Shows

1. **App Information**
   - App name
   - Archive type

2. **Actions That Would Be Performed**
   - Download URL
   - Extract location
   - Binary path
   - Symlink creation
   - Data directory linking
   - Post-install scripts

3. **No Changes Made**
   - Nothing is downloaded
   - Nothing is installed
   - No files are created
   - No symlinks are made

## Examples

### Example 1: Regular App (tar.gz)

```bash
$ ./void.py install vscode --dry-run

============================================================
 DRY RUN: Installing vscode
============================================================

App: Visual Studio Code
Type: tar.gz

Would perform these actions:
  1. Download from: https://code.visualstudio.com/sha/download?build=stable&os=linux-x64
  2. Extract to: /goinfre/user/void/apps/vscode
  3. Binary location: /goinfre/user/void/apps/vscode/VSCode-linux-x64/bin/code
  4. Create symlink: ~/bin/code -> /goinfre/user/void/apps/vscode/VSCode-linux-x64/bin/code
  5. Link data directories:
     - ~/.vscode/extensions -> /goinfre/$USER/void/data/vscode/.vscode/extensions
     - ~/.config/Code -> /goinfre/$USER/void/data/vscode/.config/Code
  6. Run post-install scripts:
     [1] {link} --install-extension ms-python.python
     [2] {link} --install-extension dbaeumer.vscode-eslint

✓ Dry run complete. No changes made.
Run without --dry-run to actually install.
```

### Example 2: AppImage

```bash
$ ./void.py install neovim --dry-run

============================================================
 DRY RUN: Installing neovim
============================================================

App: Neovim
Type: appimage

Would perform these actions:
  1. Download from: https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.appimage
  2. Extract to: /goinfre/user/void/apps/neovim
  3. Binary location: /goinfre/user/void/apps/neovim/AppRun
  4. Create symlink: ~/bin/nvim -> /goinfre/user/void/apps/neovim/AppRun

✓ Dry run complete. No changes made.
Run without --dry-run to actually install.
```

### Example 3: App with Post-Install Scripts

```bash
$ ./void.py install myapp --dry-run

============================================================
 DRY RUN: Installing myapp
============================================================

App: My Application
Type: tar.gz

Would perform these actions:
  1. Download from: https://example.com/myapp.tar.gz
  2. Extract to: /goinfre/user/void/apps/myapp
  3. Binary location: /goinfre/user/void/apps/myapp/bin/myapp
  4. Create symlink: ~/bin/myapp -> /goinfre/user/void/apps/myapp/bin/myapp
  5. Run post-install scripts:
     [1] {link} --version
     [2] bash ~/setup-myapp.sh
     [3] echo 'Installation complete!'

✓ Dry run complete. No changes made.
Run without --dry-run to actually install.
```

## Use Cases

### 1. Preview Before Installing
Check what will happen before committing to an installation:
```bash
./void.py install discord --dry-run
# Review the output
./void.py install discord  # Actually install
```

### 2. Verify Paths
Ensure binary paths and symlinks are correct:
```bash
./void.py install myapp --dry-run
# Check if binary path looks correct
```

### 3. Check Post-Install Scripts
See what scripts will run after installation:
```bash
./void.py install vscode --dry-run
# Review post-install scripts
```

### 4. Verify Data Paths
Check which directories will be symlinked:
```bash
./void.py install vscode --dry-run
# See: .vscode/extensions, .config/Code will be linked
```

### 5. Test Custom Apps
Verify custom app configuration before installing:
```bash
# Add custom app to ~/.config/void/custom_apps.json
./void.py install my-custom-app --dry-run
# Verify configuration is correct
./void.py install my-custom-app  # Install if looks good
```

## Benefits

1. **Safety** - Preview before making changes
2. **Verification** - Check paths are correct
3. **Learning** - Understand what Void does
4. **Debugging** - Identify configuration issues
5. **Confidence** - Know exactly what will happen

## Implementation

### Code Changes

**void.py - cmd_install()**
- Added `dry_run` parameter check
- Shows formatted preview of all actions
- Returns early without calling `installer.install_app()`

**Argument Parser**
- Added `--dry-run` flag to install command
- Action: `store_true` (no value needed)

### What's NOT Simulated

Dry run shows what **would** happen but doesn't:
- Check if download URL is valid
- Verify archive can be extracted
- Test if binary actually works
- Check disk space availability

It's a **preview**, not a full simulation.

## Comparison

### Without Dry Run
```bash
$ ./void.py install vscode

--- Installing vscode ---
Downloading...
[████████████████████] 100%
Extracting...
Creating symlink...
Linking data directories...
Running post-install scripts...
Successfully installed vscode!
```

### With Dry Run
```bash
$ ./void.py install vscode --dry-run

Would perform these actions:
  1. Download from: https://...
  2. Extract to: /goinfre/...
  3. Binary location: ...
  4. Create symlink: ...
  5. Link data directories: ...
  6. Run post-install scripts: ...

✓ Dry run complete. No changes made.
```

## Tips

1. **Always use dry-run first** when testing custom apps
2. **Check binary paths** - most common configuration error
3. **Verify post-install scripts** - ensure they're correct
4. **Review data paths** - make sure they're what you want
5. **Test before committing** - especially with large downloads

## Future Enhancements

- Dry-run for uninstall
- Dry-run for cleanup
- Dry-run for update
- Show estimated download size
- Check if URL is accessible
- Validate archive type matches URL
