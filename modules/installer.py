import os
import shutil
import urllib.request
import tarfile
import subprocess
from pathlib import Path
import sys
from . import apps

# Constants
# Default to /goinfre/$USER if not overridden
USER = os.environ.get("USER", "unknown")
VOID_ROOT = Path(os.getenv("VOID_ROOT", f"/goinfre/{USER}"))
APPS_DIR = VOID_ROOT / "void" / "apps"
DATA_DIR = VOID_ROOT / "void" / "data"  # New location for data syncing
BIN_DIR = Path.home() / "bin"
DESKTOP_DIR = Path.home() / ".local" / "share" / "applications"


def link_data_dirs(app_name, data_paths):
    """
    Move existing data dirs from Home to Goinfre and symlink them.
    If Home dir doesn't exist, create it in Goinfre and link.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for relative_path in data_paths:
        home_path = Path.home() / relative_path
        goinfre_path = DATA_DIR / app_name / \
            relative_path.replace("/", "_").strip(".")

        # Ensure goinfre parent exists
        goinfre_path.parent.mkdir(parents=True, exist_ok=True)

        # Case 1: Symlink already correct
        if home_path.is_symlink() and home_path.resolve() == goinfre_path.resolve():
            continue

        # Case 2: Real directory exists in Home (User has existing data)
        if home_path.exists() and not home_path.is_symlink():
            print(
                f"Moving existing data from {home_path} to {goinfre_path}...")
            # If goinfre path exists (e.g. from previous session), we merge or backup?
            # For 1337 context: locally stored usually wiped. So goinfre path likely empty or we overwrite home?
            # Safer: if goinfre exists, we might have conflict.
            # Strategy: Move Home -> Goinfre. If Goinfre exists, we assume Goinfre is more 'recent' or we just use Goinfre?
            # Actually, if user has data in Home, that's valuable.
            if goinfre_path.exists():
                print(
                    f"Warning: {goinfre_path} already exists. Backing up home version and using goinfre.")
                shutil.move(home_path, home_path.with_suffix(".bak"))
            else:
                shutil.move(home_path, goinfre_path)

        # Case 3: Nothing in Home. Create in Goinfre.
        if not goinfre_path.exists():
            goinfre_path.mkdir(parents=True, exist_ok=True)

        # Create Symlink
        # If home_path exists (folder/file), remove it (it might be empty dir created by app automatically)
        if home_path.exists() or home_path.is_symlink():
            if home_path.is_dir():
                shutil.rmtree(home_path)
            else:
                home_path.unlink()

        # Ensure parent of home_path exists (e.g. .config/)
        home_path.parent.mkdir(parents=True, exist_ok=True)

        home_path.symlink_to(goinfre_path)
        print(f"Linked data {home_path} -> {goinfre_path}")


def download_file(url, target_path):
    print(f"Downloading {url}...")
    try:
        # User-Agent is sometimes needed for some sites to allow download script
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        raise e


def extract_tar(archive_path, extract_to):
    print(f"Extracting {archive_path}...")
    try:
        # Detect mode based on suffix
        mode = "r:gz"
        if str(archive_path).endswith("tar.xz"):
            mode = "r:xz"
        elif str(archive_path).endswith("tar.bz2"):
            mode = "r:bz2"

        with tarfile.open(archive_path, mode) as tar:
            tar.extractall(path=extract_to)
        print("Extraction complete.")
    except Exception as e:
        print(f"Error extracting {archive_path}: {e}")
        raise e


def extract_deb(archive_path, extract_to):
    """
    Extract .deb package using dpkg -x (does not require root).
    Extracts to 'extract_to' directory.
    """
    print(f"Extracting DEB {archive_path}...")
    try:
        # dpkg -x <deb> <dir>
        # Ensure target dir actually exists
        Path(extract_to).mkdir(parents=True, exist_ok=True)

        cmd = ["dpkg", "-x", str(archive_path), str(extract_to)]
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True)
        print("Extraction complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting deb: {e.stderr}")
        raise Exception(f"Failed to extract deb: {e.stderr}")
    except Exception as e:
        print(f"Error extracting deb: {e}")
        raise e


def create_symlink(target, link_name):
    # Ensure bin dir exists
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    link_path = BIN_DIR / link_name

    # Remove existing link/file if it exists
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()

    print(f"Linking {target} -> {link_path}")
    link_path.symlink_to(target)


def install_appimage(app_name, source_path, install_dir):
    """
    Extract AppImage using --appimage-extract.
    This creates 'squashfs-root' which we then move to install_dir.
    """
    print(f"Extracting AppImage for {app_name}...")
    install_dir.mkdir(parents=True, exist_ok=True)

    # Move source to inside install_dir securely for operation
    temp_appimage = install_dir / "temp.AppImage"
    shutil.move(source_path, temp_appimage)

    # Make executable
    temp_appimage.chmod(0o755)

    try:
        # Run extraction
        # ./temp.AppImage --appimage-extract
        # Creates 'squashfs-root' in CWD
        cmd = [str(temp_appimage.resolve()), "--appimage-extract"]
        subprocess.run(cmd, cwd=install_dir, check=True, capture_output=True)

        # Now we have install_dir/squashfs-root
        extracted_root = install_dir / "squashfs-root"
        if not extracted_root.exists():
            raise Exception("Extraction failed: squashfs-root not found.")

        # Move contents of squashfs-root to install_dir
        # We can't rename squashfs-root to install_dir because install_dir exists and contains temp.AppImage
        # So we move contents.
        for item in extracted_root.iterdir():
            shutil.move(str(item), str(install_dir))

        # Cleanup
        shutil.rmtree(extracted_root)
        temp_appimage.unlink()
        print("AppImage extraction complete.")

    except Exception as e:
        print(f"Failed to extract AppImage: {e}")
        # Fallback? No, we want extraction. FUSE fallback not desired here.
        raise e


def find_icon(app_dir):
    """
    Attempt to find an icon in the app directory.
    Priority: .svg -> .png
    Names: icon, logo, <appname>
    """
    candidates = []

    # Simple top-down walk
    for root, dirs, files in os.walk(app_dir):
        # Limit depth
        depth = len(Path(root).relative_to(app_dir).parts)
        if depth > 3:
            del dirs[:]
            continue

        for file in files:
            if file.lower().endswith((".png", ".svg", ".xpm", ".ico")):
                candidates.append(Path(root) / file)

    # Scoring
    best_candidate = None
    best_score = 0

    for cand in candidates:
        name = cand.name.lower()
        score = 0
        if "icon" in name:
            score += 5
        if "logo" in name:
            score += 5
        if ".svg" in name:
            score += 2
        if "128" in name or "256" in name or "512" in name:
            score += 3

        if score > best_score:
            best_score = score
            best_candidate = cand

    return best_candidate


def create_desktop_entry(app_name, app_info, custom_icon=None):
    """Create a .desktop entry for the app."""
    try:
        DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

        # Paths
        desktop_file = DESKTOP_DIR / f"void_{app_name}.desktop"
        bin_path = BIN_DIR / app_info["link_name"]
        app_install_dir = APPS_DIR / app_name

        # Ensure app dir exists (might be just a link in some theoretical future, but mostly it's a dir)
        if not app_install_dir.exists():
            # Fallback if app not installed yet? Or just error?
            # Should arguably exist if we are making an entry for it.
            # But let's create it to be safe for the icon storage
            app_install_dir.mkdir(parents=True, exist_ok=True)

        # Find Icon
        if custom_icon:
            source_icon = Path(custom_icon).resolve()
            # Copy to app dir so it persists even if user deletes original
            target_icon = app_install_dir / f"custom_icon{source_icon.suffix}"
            try:
                shutil.copy(source_icon, target_icon)
                icon_path = target_icon
            except Exception as e:
                print(
                    f"Warning: Could not copy icon: {e}. Using original path.")
                icon_path = source_icon
        else:
            icon_path = find_icon(app_install_dir)

        icon_str = str(icon_path) if icon_path else "utilities-terminal"

        content = f"""[Desktop Entry]
Type=Application
Name={app_info['name']}
Exec={bin_path}
Icon={icon_str}
Terminal=false
Categories=Utility;Development;
Comment=Managed by Void
"""
        with open(desktop_file, "w") as f:
            f.write(content)

        # Make executable
        desktop_file.chmod(0o755)
        print(f"Created desktop entry: {desktop_file}")

    except Exception as e:
        print(f"Warning: Failed to create desktop entry: {e}")


def install_app(app_name):
    print(f"\n--- Installing {app_name} ---")
    app_info = apps.SUPPORTED_APPS[app_name]

    # Prepare paths
    app_install_dir = APPS_DIR / app_name

    # 1. Check if already installed
    if app_install_dir.exists():
        print(
            f"{app_name} seems to be installed at {app_install_dir}. Checking symlink...")

        # Verify binary
        if app_info["type"] == "appimage":
            # For extracted AppImages, we always use AppRun
            binary_path = app_install_dir / "AppRun"
        else:
            binary_path = app_install_dir / app_info["bin_path"]

        if binary_path.exists():
            create_symlink(binary_path, app_info["link_name"])
            create_desktop_entry(app_name, app_info)
            print(f"{app_name} is ready.")
            return
        else:
            print(f"Components missing. Re-installing...")
            shutil.rmtree(app_install_dir)

    # Create installation directory
    APPS_DIR.mkdir(parents=True, exist_ok=True)

    # Temp file for download
    filename = app_info["url"].split("/")[-1]
    # Handle query params in url if any (clean up filename)
    if "?" in filename:
        filename = "temp_download.archive"

    temp_download_path = APPS_DIR / f"{app_name}_temp_{filename}"

    # 2. Download
    download_file(app_info["url"], temp_download_path)

    # 3. Extract or Move
    try:
        if app_info["type"] == "appimage":
            # AppImage logic - Extract
            install_appimage(app_name, temp_download_path, app_install_dir)

        elif app_info["type"] == "deb":
            # DEB logic
            app_install_dir.mkdir(parents=True, exist_ok=True)
            extract_deb(temp_download_path, app_install_dir)
            temp_download_path.unlink()

        else:
            # Tarball logic
            app_install_dir.mkdir(parents=True, exist_ok=True)
            extract_tar(temp_download_path, app_install_dir)
            temp_download_path.unlink()
    except Exception as e:
        raise Exception(f"Installation failed during extraction: {e}")

    # 4. Link
    if app_info["type"] == "appimage":
        binary_path = app_install_dir / "AppRun"
    else:
        binary_path = app_install_dir / app_info["bin_path"]

    if not binary_path.exists():
        # Debug list
        files_found = []
        for root, dirs, files in os.walk(app_install_dir):
            for name in files:
                files_found.append(os.path.join(root, name))
        raise Exception(
            f"Expected binary not found at {binary_path}. Found files: {files_found[:5]}...")

    create_symlink(binary_path, app_info["link_name"])

    # 5. Create Desktop Entry
    create_desktop_entry(app_name, app_info)

    # 6. Link Data Directories
    if "data_paths" in app_info:
        link_data_dirs(app_name, app_info["data_paths"])

    print(f"Successfully installed {app_name}!")


def uninstall_app(app_name):
    print(f"\n--- Uninstalling {app_name} ---")
    if app_name not in apps.SUPPORTED_APPS:
        print(f"Unknown app: {app_name}")
        return

    app_info = apps.SUPPORTED_APPS[app_name]
    app_install_dir = APPS_DIR / app_name
    link_path = BIN_DIR / app_info["link_name"]

    # 1. Remove Symlink
    if link_path.exists() or link_path.is_symlink():
        print(f"Removing symlink: {link_path}")
        link_path.unlink()
    else:
        print(f"Symlink not found at {link_path}")

    # 1a. Remove Desktop Entry
    desktop_file = DESKTOP_DIR / f"void_{app_name}.desktop"
    if desktop_file.exists():
        print(f"Removing desktop entry: {desktop_file}")
        desktop_file.unlink()

    # 2. Remove App Directory
    if app_install_dir.exists():
        print(f"Removing app directory: {app_install_dir}")
        shutil.rmtree(app_install_dir)
    else:
        print(f"App directory not found at {app_install_dir}")

    # 3. Data Directory (Optional - currently kept for safety)
    # data_path = DATA_DIR / app_name
    # if data_path.exists():
    #     print(f"Note: Data directory preserved at {data_path}")

    print(f"Successfully uninstalled {app_name}")
