# Void - 42 School Storage Manager

**Void** is a lightweight, Python-based CLI & TUI tool designed specifically for **42 School students**. It helps you manage your limited home partition space (5GB quota) by installing heavy applications directly into the `/goinfre` partition while keeping them accessible from your shell.

![Void TUI](https://img.shields.io/badge/Interface-CLI%20%26%20TUI-blueviolet)
![Python](https://img.shields.io/badge/Language-Python%203-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-linux)

## 🚀 Key Features

*   **Smart Installation**: Installs apps to `/goinfre/$USER/void/apps/` to save home space.
*   **Seamless Integration**: Automatically symlinks binaries to `~/bin` so you can run them from anywhere.
*   **Data Syncing**: Moves heavy config/cache directories (like `~/.vscode` or `~/.config/discord`) to `/goinfre` and links them back, saving GBs of space.
*   **Interactive TUI**: A beautiful, easy-to-use Text User Interface to browse and select apps.
*   **Uninstall**: cleanly removes applications and links when you're done.
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
Just run the script without arguments:
```bash
./void.py
```
*   **Arrow Keys**: Navigate the list.
*   **Space**: Toggle selection (`[*]` for Install, `[R]` for Uninstall).
*   **Enter**: Apply changes.

### Command Line Interface (CLI)
*   **List supported apps**:
    ```bash
    ./void.py list
    ```
*   **Install an app**:
    ```bash
    ./void.py install vscode
    ./void.py install neovim
    ```
*   **Uninstall an app**:
    ```bash
    ./void.py uninstall vscode
    ```
*   **Install all favorites** (from config):
    ```bash
    ./void.py install-all
    ```

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
