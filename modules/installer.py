import os
import shutil
import urllib.request
import tarfile
from pathlib import Path
import sys
from . import apps

# Constants
# Default to /goinfre/$USER if not overridden
USER = os.environ.get("USER", "unknown")
VOID_ROOT = Path(os.getenv("VOID_ROOT", f"/goinfre/{USER}"))
APPS_DIR = VOID_ROOT / "void" / "apps" 
DATA_DIR = VOID_ROOT / "void" / "data" # New location for data syncing
BIN_DIR = Path.home() / "bin"

def link_data_dirs(app_name, data_paths):
    """
    Move existing data dirs from Home to Goinfre and symlink them.
    If Home dir doesn't exist, create it in Goinfre and link.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    for relative_path in data_paths:
        home_path = Path.home() / relative_path
        goinfre_path = DATA_DIR / app_name / relative_path.replace("/", "_").strip(".")
        
        # Ensure goinfre parent exists
        goinfre_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Case 1: Symlink already correct
        if home_path.is_symlink() and home_path.resolve() == goinfre_path.resolve():
            print(f"Data link correct: {home_path} -> {goinfre_path}")
            continue
            
        # Case 2: Real directory exists in Home (User has existing data)
        if home_path.exists() and not home_path.is_symlink():
            print(f"Moving existing data from {home_path} to {goinfre_path}...")
            # If goinfre path exists (e.g. from previous session), we merge or backup? 
            # For 42 context: locally stored usually wiped. So goinfre path likely empty or we overwrite home?
            # Safer: if goinfre exists, we might have conflict. 
            # Strategy: Move Home -> Goinfre. If Goinfre exists, we assume Goinfre is more 'recent' or we just use Goinfre?
            # Actually, if user has data in Home, that's valuable.
            if goinfre_path.exists():
                print(f"Warning: {goinfre_path} already exists. Backing up home version and using goinfre.")
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

def create_symlink(target, link_name):
    # Ensure bin dir exists
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    
    link_path = BIN_DIR / link_name
    
    # Remove existing link/file if it exists
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
        
    print(f"Linking {target} -> {link_path}")
    link_path.symlink_to(target)

def install_appimage(app_name, source_path, target_path):
    """Handle AppImage 'installation' (move and chmod)"""
    print(f"Installing AppImage for {app_name}...")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source_path, target_path)
    target_path.chmod(0o755)
    return target_path

def install_app(app_name):
    print(f"\n--- Installing {app_name} ---")
    app_info = apps.SUPPORTED_APPS[app_name]
    
    # Prepare paths
    app_install_dir = APPS_DIR / app_name
    
    # 1. Check if already installed
    if app_install_dir.exists():
        print(f"{app_name} seems to be installed at {app_install_dir}. Checking symlink...")
        
        # Verify binary
        if app_info["type"] == "appimage":
            binary_path = app_install_dir / app_info["bin_path"]
        else:
             binary_path = app_install_dir / app_info["bin_path"]

        if binary_path.exists():
            create_symlink(binary_path, app_info["link_name"])
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
            # AppImage logic
            # For AppImage, bin_path IS the file itself relative to app_install_dir
            final_binary_path = app_install_dir / app_info["bin_path"]
            install_appimage(app_name, temp_download_path, final_binary_path)
        else:
            # Tarball logic
            app_install_dir.mkdir(parents=True, exist_ok=True)
            extract_tar(temp_download_path, app_install_dir)
            temp_download_path.unlink()
    except Exception as e:
        raise Exception(f"Installation failed during extraction: {e}")
    
    # 4. Link
    binary_path = app_install_dir / app_info["bin_path"]
    
    if not binary_path.exists():
        # Debug list
        files_found = []
        for root, dirs, files in os.walk(app_install_dir):
            for name in files:
                files_found.append(os.path.join(root, name))
        raise Exception(f"Expected binary not found at {binary_path}. Found files: {files_found[:5]}...")
        
    create_symlink(binary_path, app_info["link_name"])
    
    # 5. Link Data Directories
    if "data_paths" in app_info:
        link_data_dirs(app_name, app_info["data_paths"])
        
    print(f"Successfully installed {app_name}!")
