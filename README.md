# Void - 1337 School Storage Manager

**Void** is a lightweight, Python-based CLI & TUI tool designed specifically for **1337 School students**. It helps you manage your limited home partition space (5GB quota) by installing heavy applications directly into the `/goinfre` partition while keeping them accessible from your shell.

![Void TUI](https://img.shields.io/badge/Interface-CLI%20%26%20TUI-blueviolet)
![Python](https://img.shields.io/badge/Language-Python%203-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-linux)

---

## Table of Contents

- [Features](#-key-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
  - [Interactive TUI Mode](#interactive-tui-mode)
  - [Command Line Interface](#command-line-interface)
- [Adding Custom Applications](#-adding-custom-applications)
  - [Method 1: Custom Apps Configuration (Recommended)](#method-1-custom-apps-configuration-recommended)
  - [Method 2: Adding to Source Code](#method-2-adding-to-source-code)
  - [Understanding Archive Types](#understanding-archive-types)
  - [Finding the Correct bin_path](#finding-the-correct-bin_path)
  - [Complete Configuration Reference](#complete-configuration-reference)
  - [Real-World Examples](#real-world-examples)
- [Home Directory Cleanup](#-home-directory-cleanup)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🚀 Key Features

- **💾 Smart Installation**: Installs apps to `/goinfre/$USER/void/apps/` to save precious home space
- **🔧 Custom Apps Support**: Add your own applications via JSON configuration - no code editing required
- **📦 Universal Archive Support**: Handles `.tar.gz`, `.tar.xz`, `.tar.bz2`, `.zip`, `.deb`, and `.AppImage` formats
- **🔗 Seamless Integration**: Automatically symlinks binaries to `~/bin` for instant access from anywhere
- **📁 Data Syncing**: Moves heavy config/cache directories to `/goinfre` and symlinks them back, saving GBs
- **🧹 Home Cleanup**: Analyzes and cleans safe-to-delete files to free up space in your 5GB partition
- **🎨 Interactive TUI**: Beautiful terminal interface with search, filtering, and status indicators
- **🚀 Zero Dependencies**: Uses only Python standard library - no external packages required
- **🔒 No Root Required**: Everything works without administrator privileges

---

## 📦 Installation

### Prerequisites

- Python 3.6 or higher
- Linux-based system (designed for 1337 School environment)
- `dpkg` utility (for `.deb` file extraction - usually pre-installed)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/void.git
cd void
```

### Step 2: Configure Your Shell PATH

**This step is crucial!** Without it, installed applications won't be accessible from your terminal.

Add `~/bin` to your PATH by editing your shell configuration file:

**For Zsh users:**
```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**For Bash users:**
```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Verify it worked:**
```bash
echo $PATH | grep -q "$HOME/bin" && echo "✓ PATH configured correctly" || echo "✗ PATH not configured"
```

### Step 3: Initialize Void (Optional but Recommended)

```bash
./void.py init
```

This creates the necessary configuration directories and files.

### Step 4: Run Void

```bash
./void.py
```

Or use the TUI mode (default):
```bash
./void.py tui
```

---

## 🎮 Quick Start

1. **Launch Void**: `./void.py`
2. **Search for an app**: Press `/` and type the app name
3. **Select apps**: Use `Space` to mark apps for installation
4. **Install**: Press `Enter` to process your selections
5. **Done!** Apps are now available in your terminal

---

## 📖 Usage Guide

### Interactive TUI Mode

The Text User Interface (TUI) is the recommended way to use Void. It provides an intuitive, visual way to manage your applications.

**Launch TUI:**
```bash
./void.py
# or explicitly:
./void.py tui
```

**Keyboard Controls:**

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate up/down the application list |
| `/` or `s` | Enter search mode to filter applications |
| `Space` | Toggle selection (Install `[*]`, Uninstall `[ ]`, Installed `[I]`) |
| `Enter` | Process all selected changes (install/uninstall) |
| `c` | **Cleanup** - Analyze and clean safe-to-delete files |
| `Esc` | Clear search or cancel current action |
| `q` | Quit the application |

**Status Indicators:**

- `[ ]` - Not installed, ready to install
- `[*]` - Selected for installation
- `[I]` - Already installed

### Command Line Interface

For automation, scripting, or quick operations, use the CLI commands:

#### Application Management

**List all supported applications:**
```bash
./void.py list
```

**Install a single application:**
```bash
./void.py install vscode
```

**Install multiple applications:**
```bash
./void.py install vscode discord neovim
```

**Uninstall an application:**
```bash
./void.py uninstall vscode
```

**Install all apps from your configuration:**
```bash
./void.py install-all
```

#### Archive Inspection

**Inspect an archive to find the correct `bin_path`:**
```bash
./void.py inspect https://example.com/app-linux.tar.gz
./void.py inspect https://example.com/app.AppImage --type appimage
```

The inspector will:
- Download the archive
- Extract it to a temporary location
- Show the directory structure
- Identify potential executables (sorted by relevance)
- Recommend the best `bin_path`
- Generate a ready-to-use configuration snippet

#### Desktop Entry Management

**Create or update a desktop entry with custom icon:**
```bash
./void.py entry -a vscode -i /path/to/icon.png
```

**Refresh desktop entries to fix missing icons:**
```bash
./void.py refresh-icons              # All installed apps
./void.py refresh-icons vscode       # Specific app
```

#### Home Directory Cleanup

**Analyze what can be cleaned:**
```bash
./void.py cleanup
```

**Execute cleanup (with confirmation):**
```bash
./void.py cleanup --execute
```

**Execute cleanup without confirmation:**
```bash
./void.py cleanup --execute -y
```

#### Health Check & Repair (Migration)

**Check health of installed apps** (bin symlinks, data dir symlinks):
```bash
./void.py health              # All installed apps
./void.py health vscode       # One app
```

**Repair / relink after migrating to a new post** (fixes broken symlinks like `~/.vscode`):
```bash
./void.py repair              # Repair all installed apps
./void.py repair vscode       # Repair one app
```

Use `repair` when you see errors like:
- `mkdir: cannot create directory '/home/user/.vscode': File exists`
- `ln: failed to create symbolic link '/home/user/.vscode/extensions': No such file or directory`

These happen when symlinks from the old post point to paths that no longer exist. Running `./void.py repair` removes broken symlinks and re-creates correct ones for the current post.

---

## 🛠 Adding Custom Applications

Void supports two methods for adding custom applications:

1. **Custom Apps Configuration** (Recommended) - No code editing required
2. **Source Code Modification** - For permanent additions to the project

### Method 1: Custom Apps Configuration (Recommended)

This method allows you to add applications without modifying the source code. Your custom apps persist across updates.

#### Step 1: Create the Configuration File

Create the configuration directory and file:

```bash
mkdir -p ~/.config/void
touch ~/.config/void/custom_apps.json
```

#### Step 2: Find Your Application's Download URL

Locate the direct download link for your application's Linux version. Common sources:
- Official project websites
- GitHub Releases pages
- Package repositories

**Important:** The URL must be a **direct download link** to the archive file, not a webpage.

**Examples of good URLs:**
- ✅ `https://github.com/user/app/releases/download/v1.0/app-linux-x64.tar.gz`
- ✅ `https://example.com/downloads/app.AppImage`
- ✅ `https://example.com/packages/app.deb`

**Examples of bad URLs:**
- ❌ `https://example.com/download` (redirects to download page)
- ❌ `https://github.com/user/app/releases` (releases page, not direct file)

#### Step 3: Determine the Archive Type

Void supports these archive types:

| Type | Extension | Description |
|------|-----------|-------------|
| `tar.gz` | `.tar.gz`, `.tgz` | Compressed tar archive (most common) |
| `tar.xz` | `.tar.xz` | XZ-compressed tar archive |
| `tar.bz2` | `.tar.bz2` | BZIP2-compressed tar archive |
| `zip` | `.zip` | ZIP archive |
| `deb` | `.deb` | Debian package |
| `appimage` | `.AppImage` | AppImage single-file application |

The type is usually auto-detected from the URL, but you can specify it manually if needed.

#### Step 4: Find the Correct `bin_path`

**This is the most important step!** The `bin_path` tells Void where to find the executable inside the extracted archive.

##### Option A: Use the Inspector Tool (Easiest)

The inspector automatically finds the correct `bin_path` for you:

```bash
./void.py inspect https://example.com/download/app-linux.tar.gz
```

**Example Output:**
```
============================================================
 Archive Structure Analysis
============================================================

Archive Type: tar.gz
Root Directory: app-v1.0.0

Directory Structure:
------------------------------------------------------------
app-v1.0.0/
├── bin/
│   └── app [EXEC] (15,234,567 bytes)
├── lib/
├── share/
└── README.txt

============================================================
 Potential Binaries (sorted by relevance)
============================================================

1. ★★★★★ app-v1.0.0/bin/app [EXECUTABLE] (14.5 MB)
   Score: 38, Parent: bin

RECOMMENDED bin_path:
  "bin_path": "app-v1.0.0/bin/app"

Example Configuration:
    "my-app": {
        "name": "My App",
        "url": "https://example.com/download/app-linux.tar.gz",
        "type": "tar.gz",
        "bin_path": "app-v1.0.0/bin/app",
        "link_name": "myapp"
    }
```

**How the Inspector Works:**

The inspector uses an intelligent scoring system to identify the main executable:

1. **Base Scoring**: Executables get points for being in `bin/` directories, having execute permissions, etc.
2. **Size Analysis**: Larger files (main apps) score higher than smaller helper utilities
3. **Name Analysis**: 
   - Simple names (no hyphens) score higher
   - Names containing "worker", "helper", "daemon" get penalized
   - Shorter names are preferred
4. **Pattern Matching**: Recognizes common executable patterns

The highest-scoring executable is recommended as the `bin_path`.

##### Option B: Manual Inspection

If you prefer to find it manually:

1. **Download the archive** to a temporary location
2. **Extract it** using your system's tools:
   ```bash
   tar -xzf app-linux.tar.gz
   # or
   unzip app.zip
   # or
   dpkg -x app.deb extracted/
   ```
3. **Explore the structure** to find the executable:
   ```bash
   find extracted/ -type f -executable
   ```
4. **Note the relative path** from the archive root

**Common Locations:**
- `app-name/bin/app-name`
- `app-name/app-name`
- `usr/bin/app-name` (for `.deb` packages)
- `AppRun` (for AppImages after extraction)

#### Step 5: Create Your Configuration

Edit `~/.config/void/custom_apps.json` and add your app definition:

```json
{
    "my-custom-app": {
        "name": "My Custom Application",
        "url": "https://example.com/download/app-linux-x64.tar.gz",
        "type": "tar.gz",
        "bin_path": "app-v1.0.0/bin/app",
        "link_name": "myapp",
        "data_paths": [
            ".config/myapp",
            ".cache/myapp"
        ]
    }
}
```

#### Step 6: Verify Your Configuration

Test your configuration by listing apps:

```bash
./void.py list
```

Your custom app should appear in the list. If there are JSON syntax errors, Void will display them.

#### Step 7: Install Your Custom App

```bash
./void.py install my-custom-app
```

Or use the TUI and search for your app name.

### Method 2: Adding to Source Code

For permanent additions that will be included in the project, edit `modules/apps.py`.

#### Step 1: Open the Apps File

```bash
nano modules/apps.py
# or use your preferred editor
```

#### Step 2: Find the `SUPPORTED_APPS` Dictionary

Locate the `SUPPORTED_APPS` dictionary (usually near the top of the file).

#### Step 3: Add Your App Entry

Add your app following the same structure as existing entries. Choose an appropriate category section:

```python
SUPPORTED_APPS = {
    # ... existing apps ...
    
    # --- Your Category ---
    "my-app-id": {
        "name": "My Application Name",
        "url": "https://example.com/download/app-linux.tar.gz",
        "type": "tar.gz",
        "bin_path": "app-folder/bin/app",
        "link_name": "myapp",
        "data_paths": [
            ".config/myapp"
        ]
    },
}
```

**Important Notes:**
- Use a unique `app-id` (no spaces, lowercase, hyphens allowed)
- Follow the existing code style and indentation
- Place your entry in an appropriate category section
- Add a comma after your entry (except for the last one)

#### Step 4: Test Your Addition

```bash
./void.py list | grep my-app-id
./void.py install my-app-id
```

### Understanding Archive Types

Different archive types require different handling:

#### Tarballs (`.tar.gz`, `.tar.xz`, `.tar.bz2`)

**Most common format.** Usually extracts to a single folder containing the application.

**Example structure:**
```
app-v1.0.0/
├── bin/
│   └── app
├── lib/
├── share/
└── README.txt
```

**bin_path:** `app-v1.0.0/bin/app`

#### ZIP Archives (`.zip`)

Similar to tarballs, extracts to a folder structure.

**Example structure:**
```
app/
├── app.exe
├── lib/
└── config/
```

**bin_path:** `app/app.exe`

#### Debian Packages (`.deb`)

Extracts to a Linux filesystem structure.

**Example structure:**
```
usr/
├── bin/
│   └── appname
├── share/
│   └── appname/
└── lib/
```

**bin_path:** `usr/bin/appname`

**Note:** For `.deb` packages, the `bin_path` usually starts with `usr/`.

#### AppImages (`.AppImage`)

Single-file applications that are extracted internally.

**Important:** For AppImages, use the **filename** as `bin_path`:
- Download: `MyApp.AppImage`
- `bin_path`: `MyApp.AppImage`

Void automatically extracts AppImages and links to the internal `AppRun` executable.

### Finding the Correct `bin_path`

The `bin_path` is the **relative path** from the archive root to the executable file.

#### Rules for `bin_path`:

1. **Always relative** - Don't include leading slashes
2. **Case-sensitive** - Match the exact case in the archive
3. **Include the root folder** - If archive extracts to `app-v1.0.0/`, include it
4. **Path to executable** - Not the directory, the actual file

#### Examples:

**Archive structure:**
```
myapp-2.0/
└── bin/
    └── myapp
```

**Correct `bin_path`:** `myapp-2.0/bin/myapp` ✅

**Incorrect `bin_path`:** 
- `/myapp-2.0/bin/myapp` ❌ (leading slash)
- `bin/myapp` ❌ (missing root folder)
- `myapp-2.0/bin/` ❌ (points to directory, not file)

#### Common Patterns:

| Archive Structure | bin_path Example |
|-------------------|------------------|
| `app/bin/app` | `app/bin/app` |
| `app-v1.0/app` | `app-v1.0/app` |
| `usr/bin/appname` | `usr/bin/appname` |
| `AppFolder/AppRun` | `AppFolder/AppRun` |
| `app.sh` (root level) | `app.sh` |

### Complete Configuration Reference

#### Required Fields

**`name`** (string, required)
- Human-readable application name
- Displayed in the TUI and CLI output
- Example: `"Visual Studio Code"`

**`url`** (string, required)
- Direct download URL to the archive file
- Must be accessible without authentication
- Example: `"https://code.visualstudio.com/sha/download?build=stable&os=linux-x64"`

**`type`** (string, required)
- Archive format type
- Valid values: `"tar.gz"`, `"tar.xz"`, `"tar.bz2"`, `"zip"`, `"deb"`, `"appimage"`
- Example: `"tar.gz"`

**`bin_path`** (string, required)
- Relative path to the executable inside the extracted archive
- Use the inspector tool to find this automatically
- Example: `"VSCode-linux-x64/bin/code"`

**`link_name`** (string, required)
- Command name created in `~/bin`
- This is what you'll type in the terminal to run the app
- Should be short and memorable
- Example: `"code"` (allows running `code` command)

#### Optional Fields

**`data_paths`** (array of strings, optional)
- List of directories in your home folder that the app uses heavily
- These will be moved to `/goinfre` and symlinked back
- Saves significant space for apps with large config/cache directories
- Paths are relative to home directory (start with `.`)
- Example: `[".config/Code", ".vscode"]`

**`post_install`** (array of strings, optional)
- Shell commands to run after successful installation
- Useful for installing extensions, configuring settings, or downloading additional resources
- Commands are executed in order, with 5-minute timeout per command
- Available placeholders:
  - `{bin}` - Full path to the installed binary
  - `{link}` - Full path to the symlink in ~/bin
- Example: `["{link} --install-extension ms-python.python", "echo 'Setup complete'"]`

**When to use `data_paths`:**
- Apps with large extension directories (IDEs)
- Apps with extensive cache (browsers, editors)
- Apps that store user data in home directory
- Any directory >100MB in your home folder

**Common `data_paths` patterns:**
```json
"data_paths": [
    ".config/appname",      // Configuration directory
    ".cache/appname",       // Cache directory
    ".local/share/appname", // Application data
    ".appname"              // Root-level app directory
]
```

### Real-World Examples

#### Example 1: Simple Tarball Application

**App:** A command-line tool distributed as `.tar.gz`

**Archive structure:**
```
mytool-1.2.3/
├── mytool
├── README.md
└── LICENSE
```

**Configuration:**
```json
{
    "mytool": {
        "name": "My Tool",
        "url": "https://example.com/releases/mytool-1.2.3-linux-x64.tar.gz",
        "type": "tar.gz",
        "bin_path": "mytool-1.2.3/mytool",
        "link_name": "mytool"
    }
}
```

#### Example 2: AppImage Application

**App:** A GUI application distributed as `.AppImage`

**Configuration:**
```json
{
    "myapp": {
        "name": "My Application",
        "url": "https://example.com/releases/MyApp-2.0-x86_64.AppImage",
        "type": "appimage",
        "bin_path": "MyApp-2.0-x86_64.AppImage",
        "link_name": "myapp"
    }
}
```

**Note:** For AppImages, `bin_path` is the filename. Void handles extraction internally.

#### Example 3: Debian Package with Data Paths

**App:** An IDE that stores extensions and cache in home directory

**Configuration:**
```json
{
    "myide": {
        "name": "My IDE",
        "url": "https://example.com/packages/myide-1.0.deb",
        "type": "deb",
        "bin_path": "usr/bin/myide",
        "link_name": "myide",
        "data_paths": [
            ".config/myide",
            ".cache/myide",
            ".myide"
        ]
    }
}
```

#### Example 4: Application with Complex Structure

**App:** Application with nested directory structure

**Archive structure:**
```
app-release/
├── app-release/
│   ├── bin/
│   │   └── app
│   ├── lib/
│   └── share/
└── install.sh
```

**Configuration:**
```json
{
    "complex-app": {
        "name": "Complex Application",
        "url": "https://example.com/app-release.tar.gz",
        "type": "tar.gz",
        "bin_path": "app-release/app-release/bin/app",
        "link_name": "capp"
    }
}
```

#### Example 5: IDE with Extensions (Post-Install Scripts)

**App:** VSCode with automatic extension installation

**Configuration:**
```json
{
    "vscode": {
        "name": "Visual Studio Code",
        "url": "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64",
        "type": "tar.gz",
        "bin_path": "VSCode-linux-x64/bin/code",
        "link_name": "code",
        "data_paths": [
            ".vscode/extensions",
            ".config/Code"
        ],
        "post_install": [
            "{link} --install-extension ms-python.python",
            "{link} --install-extension dbaeumer.vscode-eslint",
            "{link} --install-extension esbenp.prettier-vscode",
            "echo 'VSCode configured with Python, ESLint, and Prettier'"
        ]
    }
}
```

**What happens:**
1. VSCode is installed to `/goinfre`
2. Binary is symlinked to `~/bin/code`
3. Extensions directory moved to `/goinfre` and symlinked
4. Post-install scripts run automatically:
   - Installs Python extension
   - Installs ESLint extension
   - Installs Prettier extension
   - Prints confirmation message

### Troubleshooting Custom Apps

#### Problem: App doesn't appear in list

**Solutions:**
1. Check JSON syntax: `cat ~/.config/void/custom_apps.json | python3 -m json.tool`
2. Verify file location: `ls -la ~/.config/void/custom_apps.json`
3. Check for duplicate keys (JSON doesn't allow duplicate keys)

#### Problem: Installation fails with "binary not found"

**Solutions:**
1. Use inspector to verify `bin_path`: `./void.py inspect <url>`
2. Check if archive structure changed (version update)
3. Verify `bin_path` is relative (no leading slash)
4. Ensure `bin_path` points to a file, not a directory

#### Problem: Post-install script fails

**Solutions:**
1. Check script syntax and commands are valid
2. Verify placeholders `{bin}` and `{link}` are used correctly
3. Test command manually: `~/bin/<link_name> <command>`
4. Check script output in installation logs
5. Ensure script doesn't require user interaction (use non-interactive flags)

#### Problem: App installs but command doesn't work

**Solutions:**
1. Verify PATH is configured: `echo $PATH | grep "$HOME/bin"`
2. Check symlink exists: `ls -la ~/bin/<link_name>`
3. Test binary directly: `~/bin/<link_name> --version`
4. Check file permissions: `ls -l /goinfre/$USER/void/apps/<app-name>/<bin_path>`

#### Problem: Archive type detection fails

**Solutions:**
1. Specify type manually: `./void.py inspect <url> --type <type>`
2. Check URL contains type hint (e.g., `/deb/` in path)
3. Verify archive format matches specified type

---

## 🧹 Home Directory Cleanup

Void includes a powerful cleanup feature to help you free up space in your 5GB home partition.

### What Gets Cleaned

The cleanup tool identifies and removes safe-to-delete files:

**Browser Caches:**
- Firefox cache (`~/.cache/mozilla`)
- Chrome/Chromium cache (`~/.cache/google-chrome`, `~/.cache/chromium`)
- Other browser caches

**Application Caches:**
- Python: `~/.cache/pip`, `~/.cache/pipenv`
- Node.js: `~/.cache/npm`, `~/.cache/yarn`
- Rust: `~/.cache/cargo`
- Go: `~/.cache/go-build`

**IDE/Editor Caches:**
- VSCode: `~/.cache/vscode`, `~/.cache/Code`
- JetBrains IDEs: `~/.cache/JetBrains`
- Sublime Text: `~/.cache/sublime-text`

**Build Artifacts:**
- Python: `__pycache__/`, `*.pyc`, `.pytest_cache/`
- Node.js: `node_modules/` (can be reinstalled)
- Rust: `target/`
- Other: `dist/`, `build/`, `.gradle/`, `.m2/`

**System Files:**
- Trash/Recycle bin: `~/.local/share/Trash`
- Thumbnail cache: `~/.cache/thumbnails`
- Font cache: `~/.cache/fontconfig`
- Log files: `*.log`

### Usage

**In TUI Mode:**
1. Launch Void: `./void.py`
2. Press `c` to enter cleanup mode
3. Review what will be cleaned
4. Press `y` to confirm or any other key to cancel

**In CLI Mode:**

Analyze what can be cleaned:
```bash
./void.py cleanup
```

Execute cleanup with confirmation:
```bash
./void.py cleanup --execute
```

Execute cleanup without confirmation:
```bash
./void.py cleanup --execute -y
```

### Safety Features

- ✅ **Only safe files**: Only removes cache, temporary files, and build artifacts
- ✅ **Preview before delete**: Always shows what will be deleted
- ✅ **Confirmation required**: Asks for confirmation unless `-y` flag is used
- ✅ **Reversible**: Build artifacts can be regenerated (e.g., `npm install`)

### Example Output

```
============================================================
 Analyzing Home Directory Space Usage
============================================================

Disk Usage for /home/user:
  Total: 4.65 GB
  Used:  3.85 GB (82.8%)
  Free:  800.00 MB

Found 47 items that can be cleaned:
  Total cleanable: 1.2 GB

  Browser Cache: 12 items (450.5 MB)
    - .cache/mozilla: 250.3 MB
    - .cache/google-chrome: 200.2 MB
  
  Build Artifacts: 8 items (650.3 MB)
    - project1/node_modules: 400.1 MB
    - project2/__pycache__: 50.2 MB
  
  Application Cache: 15 items (100.2 MB)
    - .cache/pip: 45.3 MB
    - .cache/npm: 54.9 MB

Run 'void cleanup --execute' to clean these files.
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "Command not found" after installation

**Problem:** Installed apps aren't accessible from terminal.

**Solutions:**
1. Verify PATH configuration:
   ```bash
   echo $PATH | grep -q "$HOME/bin" && echo "✓ PATH OK" || echo "✗ PATH missing"
   ```
2. Add to PATH if missing:
   ```bash
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
   source ~/.zshrc  # or source ~/.bashrc
   ```
3. Restart your terminal
4. Verify symlink exists: `ls -la ~/bin/<app-name>`

#### Download fails (404/403 errors)

**Problem:** Archive URL is no longer valid.

**Solutions:**
1. Check if the app's download URL has changed
2. Visit the official website to find the new URL
3. Update the URL in your configuration:
   - Custom apps: Edit `~/.config/void/custom_apps.json`
   - Source code: Edit `modules/apps.py`
4. Use the inspector to verify the new URL works:
   ```bash
   ./void.py inspect <new-url>
   ```

#### App crashes or doesn't start

**Problem:** Installed application fails to run.

**Solutions:**
1. Test the binary directly:
   ```bash
   ~/bin/<app-name> --version
   # or
   /goinfre/$USER/void/apps/<app-name>/<bin_path>
   ```
2. Check for error messages in terminal output
3. Verify the `bin_path` is correct (use inspector)
4. Check file permissions:
   ```bash
   ls -l /goinfre/$USER/void/apps/<app-name>/<bin_path>
   ```
5. Ensure all dependencies are installed (some apps require system libraries)

#### Migration to a new post (broken symlinks)

**Problem:** After changing post (workspace), apps fail to launch or you see:
- `mkdir: cannot create directory '/home/user/.vscode': File exists`
- `ln: failed to create symbolic link '/home/user/.vscode/extensions': No such file or directory`

**Cause:** Data dirs (e.g. `~/.vscode`) were symlinks to the old post’s goinfre path. After migration they are broken.

**Solutions:**
1. **Check health:**
   ```bash
   ./void.py health
   ```
2. **Repair all installed apps** (removes broken symlinks and re-creates correct ones):
   ```bash
   ./void.py repair
   ```
3. To repair only one app:
   ```bash
   ./void.py repair vscode
   ```

#### Low disk space warnings

**Problem:** Home partition is running out of space.

**Solutions:**
1. Run cleanup analysis:
   ```bash
   ./void.py cleanup
   ```
2. Execute cleanup:
   ```bash
   ./void.py cleanup --execute
   ```
3. Check for large files that can be moved to `/goinfre`
4. Review installed apps and uninstall unused ones
5. Use `du -sh ~/*` to identify large directories

#### Archive extraction fails

**Problem:** Inspector or installer fails to extract archive.

**Solutions:**
1. Verify archive type is correct:
   ```bash
   file downloaded-archive.tar.gz
   ```
2. Try specifying type manually:
   ```bash
   ./void.py inspect <url> --type <correct-type>
   ```
3. Check if archive is corrupted (re-download)
4. Verify you have write permissions in `/goinfre`

#### Custom app doesn't appear in list

**Problem:** Custom app configuration isn't being loaded.

**Solutions:**
1. Verify file exists and is readable:
   ```bash
   ls -la ~/.config/void/custom_apps.json
   ```
2. Check JSON syntax:
   ```bash
   python3 -m json.tool ~/.config/void/custom_apps.json
   ```
3. Ensure no duplicate keys in JSON
4. Check file permissions (should be readable)
5. Restart Void to reload configuration

#### AppImage extraction fails

**Problem:** AppImage can't be extracted (FUSE issues).

**Solutions:**
1. This shouldn't happen - Void automatically extracts AppImages
2. Verify AppImage is not corrupted
3. Check if AppImage requires specific system libraries
4. Try downloading a different version

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Void prints detailed error messages
2. **Use verbose mode**: Some commands support `-v` flag
3. **Inspect archives**: Use `./void.py inspect` to debug archive issues
4. **Verify configuration**: Check JSON syntax and file locations

---

## 📝 License

This project is open source. Feel free to modify and share!

---

## 🙏 Acknowledgments

Designed specifically for 1337 School students to help manage the 5GB home partition constraint. Special thanks to the open-source community for inspiration and tools.

---

**Made with ❤️ for the 1337 School community**
