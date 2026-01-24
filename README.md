# Void - 1337 School Storage Manager

**Void** is a lightweight, Python-based CLI & TUI tool designed specifically for **1337 School students**. It helps you manage your limited home partition space (5GB quota) by installing heavy applications directly into the `/goinfre` partition while keeping them accessible from your shell.

![Void TUI](https://img.shields.io/badge/Interface-CLI%20%26%20TUI-blueviolet)
![Python](https://img.shields.io/badge/Language-Python%203-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-linux)

## 🚀 Key Features

*   **Smart Installation**: Installs apps to `/goinfre/$USER/void/apps/` to save home space.
*   **Custom Apps**: Add your own applications by creating a `custom_apps.json` config!
*   **No FUSE Required**: AppImages are automatically extracted, making them compatible with strict environments like 1337 `goinfre`.
*   **Seamless Integration**: Automatically symlinks binaries to `~/bin` so you can run them from anywhere.
*   **Data Syncing**: Moves heavy config/cache directories (like `~/.vscode` or `~/.config/discord`) to `/goinfre` and links them back, saving GBs of space.
*   **Interactive TUI**: A beautiful terminal interface with **Search**, Filtering, and Status indicators.
*   **Uninstall**: Cleanly removes applications and links when you're done.
*   **Portable**: No root access required. No dependencies (uses standard Python library).

---

## 📦 Installation

1.  **Clone the Repository**:
    Download the tool to your preferred location (e.g., inside your projects folder).
    ```bash
    git clone https://github.com/your-username/void.git
    cd void
    ```

2.  **Add to PATH (Crucial Step)**:
    For the installed apps (like `code`, `nvim`, `discord`) to work, your shell needs to know where to look. Void puts links in `~/bin`.
    
    Add this line to your shell configuration (`~/.zshrc` or `~/.bashrc`):
    ```bash
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

3.  **Run Void**:
    You can now run the tool directly:
    ```bash
    ./void.py
    ```

---

## 🎮 Usage

You can use Void in two modes: **Interactive TUI** (Recommended) or **Command Line**.

### Interactive Mode (TUI)
The recommended way to use Void.
```bash
./void.py
```
**Controls:**
*   **`↑` / `↓`**: Navigate the application list.
*   **`/` or `s`**: **Search** for an application by name.
*   **`Space`**: Toggle selection to Install `[*]`, Uninstall `[ ]`, or Keep `[I]`.
*   **`Enter`**: Process all selected changes (Install/Uninstall).
*   **`Esc`**: Clear search or cancel action.
*   **`q`**: Quit.

### Command Line Interface (CLI)
Automation-friendly commands.

*   **List all apps**:
    ```bash
    ./void.py list
    ```
*   **Install applications**:
    ```bash
    ./void.py install vscode
    ./void.py install discord neovim
    ```
*   **Uninstall applications**:
    ```bash
    ./void.py uninstall vscode
    ```
*   **Install from Config**:
    Restore your favorite apps defined in `~/.config/void/apps.json`:
    ```bash
    ./void.py install-all
    ```
*   **Update Desktop Entry**:
    Fix a broken icon or update properties:
    ```bash
    ./void.py entry -a vscode -i /path/to/icon.png
    ```

## 🛠 Adding Custom Apps

You can add your own applications without editing the code!
Create a file at `~/.config/void/custom_apps.json` and add your definitions.

### Example `custom_apps.json`
```json
{
    "my-app": {
        "name": "My Custom App",
        "url": "https://example.com/download/app-linux.tar.gz",
        "type": "tar.gz",
        "bin_path": "AppFolder/bin/executable",
        "link_name": "myapp",
        "data_paths": [
            ".config/myapp"
        ]
    }
}
```

### Configuration Keys Explained

*   **`name`** (Required): The human-readable name shown in the TUI.
*   **`url`** (Required): Direct download link to the file.
    *   Supported formats: `.tar.gz`, `.tar.xz`, `.zip`, `.deb`, `.AppImage`.
*   **`type`** (Required): The archive type.
    *   `tar.gz`, `tar.xz`, `zip`: Will be extracted.
    *   `appimage`: Will be downloaded, made executable, and extracted (to avoid FUSE issues).
    *   `deb`: Will be extracted using `dpkg -x`.
*   **`bin_path`** (Required): The relative path to the binary *inside* the extracted archive.
    *   For **AppImages**, always use the filename itself (e.g., `MyApp.AppImage`). The installer automatically links to the extracted `AppRun`.
    *   For **Tarballs/Zips**, explore the archive to find the executable path (e.g., `StartFolder/bin/start.sh`).
*   **`link_name`** (Required): The name of the command created in `~/bin`.
    *   Example: `"link_name": "code"` allows you to run `code` from the terminal.
*   **`data_paths`** (Optional): A list of folders in your Home directory that this app uses heavily (config, cache, etc.).
    *   **Void Magic**: These folders will be moved to `/goinfre` and symlinked back to `~`.
    *   Example: `[".config/Code", ".vscode"]` saves GBs of space for VSCode.

---

## 🛠️ How to Add Your Own Apps

Even if you don't know Python, you can easily add support for new applications. All app definitions are stored in `modules/apps.py`.

### Step-by-Step Guide

1.  Open `modules/apps.py` in your text editor.
2.  Find the `SUPPORTED_APPS` dictionary.
3.  Add a new entry following this template:

```python
    "my-app-name": {
        "name": "My Cool App",
        "url": "https://example.com/download/myapp-linux-x64.tar.gz",
        "type": "tar.gz",           # Supported: tar.gz, tar.xz, tar.bz2, appimage, zip
        "bin_path": "myapp/bin/run", # Path to the executable INSIDE the downloaded archive
        "link_name": "myapp"        # The command you want to type in terminal
    },
```

### Explaining the Fields
*   **Key (`"my-app-name"`)**: A unique ID for the app (no spaces).
*   **`"name"`**: Human-readable name shown in the menu.
*   **`"url"`**: Direct download link (must end in .tar.gz, .AppImage, etc.).
*   **`"type"`**: Archive type. use `"appimage"` for single-file executables.
*   **`"bin_path"`**: 
    *   For **AppImages**: Just the filename (e.g., `MyApp.AppImage`).
    *   For **Archives (.tar.gz)**: The path to the executable inside the folder. *Tip: Download and extract it manually once to check the folder structure.*
*   **`"link_name"`**: The short command you want to use (e.g., `code`, `nvim`).
*   **`"data_paths"`** *(Optional)*: List of heavy folders in your Home directory to move to goinfre.
    ```python
    "data_paths": [".config/myapp", ".cache/myapp"]
    ```

### Example: Adding a new Tool
Let's say you want to add a tool called "SuperTool".
1.  **URL**: You find the link: `https://supertool.com/dl/supertool-v1.tar.gz`.
2.  **Structure**: You check inside and see it extracts to a folder `supertool-v1/` containing a binary `runner`.
3.  **Entry**:
    ```python
    "supertool": {
        "name": "Super Tool",
        "url": "https://supertool.com/dl/supertool-v1.tar.gz",
        "type": "tar.gz",
        "bin_path": "supertool-v1/runner",
        "link_name": "supertool"
    }
    ```

---

## 🔧 Troubleshooting

*   **"Command not found"**:
    *   Ensure you ran the `export PATH...` step above.
    *   Restart your terminal.
*   **Download fails (404/403)**:
    *   The app's URL might have changed. Check `modules/apps.py` and update the `"url"` field with a fresh link found online.
*   **App crashes**:
    *   Try running the installed binary directly from `~/bin/` to see error messages.

---

## 📝 License
This project is open source. Feel free to modify and share!
