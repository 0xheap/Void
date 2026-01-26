"""
Archive Inspector - Helps users find the correct bin_path for custom apps.
Downloads, extracts, and analyzes archive structure to identify executables.
"""

import os
import shutil
import tempfile
import tarfile
import zipfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import urllib.request


def download_file(url: str, target_path: Path) -> None:
    """Download a file from URL."""
    print(f"Downloading {url}...")
    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        raise e


def extract_archive(archive_path: Path, extract_to: Path, archive_type: str) -> None:
    """Extract archive based on type."""
    extract_to.mkdir(parents=True, exist_ok=True)
    
    try:
        if archive_type == "zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(path=extract_to)
        elif archive_type == "deb":
            cmd = ["dpkg", "-x", str(archive_path), str(extract_to)]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        elif archive_type == "appimage":
            # For AppImages, we extract using --appimage-extract
            archive_path.chmod(0o755)
            cmd = [str(archive_path), "--appimage-extract"]
            subprocess.run(cmd, cwd=extract_to, check=True, capture_output=True)
            # Move squashfs-root contents to extract_to
            squashfs_root = extract_to / "squashfs-root"
            if squashfs_root.exists():
                for item in squashfs_root.iterdir():
                    shutil.move(str(item), str(extract_to))
                shutil.rmtree(squashfs_root)
        else:
            # Tarball (tar.gz, tar.xz, tar.bz2)
            mode = "r:gz"
            if archive_type == "tar.xz":
                mode = "r:xz"
            elif archive_type == "tar.bz2":
                mode = "r:bz2"
            
            with tarfile.open(archive_path, mode) as tar:
                tar.extractall(path=extract_to)
        
        print(f"Extracted to {extract_to}")
    except Exception as e:
        # If extraction fails, try to detect actual type from file content
        error_msg = str(e).lower()
        if "not a gzip file" in error_msg or "bad magic number" in error_msg:
            # File might be a different type than detected
            # Try to detect from file signature
            with open(archive_path, 'rb') as f:
                header = f.read(4)
                if header.startswith(b'PK\x03\x04'):
                    raise Exception(f"File appears to be a ZIP archive, not {archive_type}. Try: --type zip")
                elif header.startswith(b'\x1f\x8b'):
                    raise Exception(f"File appears to be a gzip archive, not {archive_type}. Try: --type tar.gz")
                elif header.startswith(b'!<arch>') or header.startswith(b'0\x00'):
                    raise Exception(f"File appears to be a DEB archive, not {archive_type}. Try: --type deb")
        raise e


def is_executable(path: Path) -> bool:
    """Check if a file is executable."""
    if not path.is_file():
        return False
    return os.access(path, os.X_OK) or path.suffix in ['.sh', '.AppImage'] or 'AppRun' in path.name


def is_likely_binary(path: Path) -> bool:
    """Check if a file is likely a binary executable."""
    if not path.is_file():
        return False
    
    name = path.name.lower()
    
    # Common binary patterns
    binary_patterns = [
        # No extension (common for Linux binaries)
        not path.suffix,
        # Common executable names
        name in ['apprun', 'run', 'start', 'launch', 'main'],
        # Common binary extensions
        path.suffix in ['.bin', '.exe', '.appimage'],
        # Scripts
        path.suffix in ['.sh', '.py'],
        # In common binary directories
        path.parent.name.lower() in ['bin', 'usr/bin', 'usr/local/bin'],
    ]
    
    return any(binary_patterns)


def find_executables(root_dir: Path, max_depth: int = 5) -> List[Tuple[Path, Dict]]:
    """
    Find all potential executable files in the extracted archive.
    Returns list of (path, metadata) tuples.
    """
    executables = []
    root_str = str(root_dir)
    
    for root, dirs, files in os.walk(root_dir):
        depth = len(Path(root).relative_to(root_dir).parts)
        if depth > max_depth:
            dirs[:] = []  # Don't recurse deeper
            continue
        
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(root_dir)
            
            # Skip hidden files and common non-executables
            if file.startswith('.') or file.endswith(('.txt', '.md', '.json', '.xml', '.conf', '.config')):
                continue
            
            file_name = file_path.name.lower()
            file_name_no_ext = file_path.stem.lower()
            
            metadata = {
                'is_executable': is_executable(file_path),
                'is_likely_binary': is_likely_binary(file_path),
                'size': file_path.stat().st_size if file_path.exists() else 0,
                'parent_dir': file_path.parent.name,
                'name': file_name,
            }
            
            # Score for relevance
            score = 0
            
            # Base scores
            if metadata['is_executable']:
                score += 10
            if metadata['is_likely_binary']:
                score += 5
            if metadata['parent_dir'].lower() in ['bin', 'usr/bin', 'usr/local/bin']:
                score += 8
            if not file_path.suffix:  # No extension often means binary
                score += 3
            
            # Prefer larger executables (main apps are usually bigger)
            # Normalize size score: 1 point per 10MB, max 10 points
            size_mb = metadata['size'] / (1024 * 1024)
            score += min(int(size_mb / 10), 10)
            
            # Penalize helper/worker executables
            helper_keywords = ['worker', 'helper', 'daemon', 'service', 'gfx', 'gui', 
                             'backend', 'server', 'client', 'plugin', 'extension',
                             'launcher', 'wrapper', 'shim', 'proxy']
            for keyword in helper_keywords:
                if keyword in file_name:
                    score -= 15  # Strong penalty
                    break
            
            # Prefer simpler names (fewer hyphens/underscores)
            hyphen_count = file_name.count('-') + file_name.count('_')
            if hyphen_count == 0:
                score += 5  # Simple name bonus
            elif hyphen_count >= 3:
                score -= 5  # Penalty for complex names
            
            # Prefer shorter names (main executables are usually concise)
            if len(file_name_no_ext) <= 10:
                score += 3
            elif len(file_name_no_ext) > 25:
                score -= 3
            
            # Prefer common main executable patterns
            if file_name_no_ext in ['run', 'start', 'main', 'app']:
                score += 5
            if file_name_no_ext.endswith('sync') or file_name_no_ext.endswith('app'):
                score += 2
            
            # Ensure score doesn't go negative
            score = max(score, 0)
            
            metadata['score'] = score
            
            if score > 0:  # Only include files with some relevance
                executables.append((rel_path, metadata))
    
    # Sort by score (highest first)
    executables.sort(key=lambda x: x[1]['score'], reverse=True)
    return executables


def get_directory_tree(root_dir: Path, max_depth: int = 3, max_items: int = 50) -> List[str]:
    """Generate a directory tree representation."""
    tree = []
    items_shown = 0
    
    def walk_tree(path: Path, prefix: str = "", depth: int = 0):
        nonlocal items_shown
        if items_shown >= max_items or depth > max_depth:
            return
        
        if path.is_dir():
            # Show directory
            tree.append(f"{prefix}{path.name}/")
            items_shown += 1
            
            # List contents (limited)
            try:
                entries = sorted(path.iterdir())[:10]  # Limit to 10 per directory
                for i, entry in enumerate(entries):
                    is_last = i == len(entries) - 1
                    new_prefix = prefix + ("└── " if is_last else "├── ")
                    walk_tree(entry, new_prefix, depth + 1)
                    if items_shown >= max_items:
                        break
            except PermissionError:
                pass
        else:
            # Show file
            size = path.stat().st_size if path.exists() else 0
            size_str = f" ({size:,} bytes)" if size > 0 else ""
            exec_marker = " [EXEC]" if is_executable(path) else ""
            tree.append(f"{prefix}{path.name}{size_str}{exec_marker}")
            items_shown += 1
    
    walk_tree(root_dir)
    
    if items_shown >= max_items:
        tree.append("... (truncated)")
    
    return tree


def detect_archive_type(url: str) -> str:
    """Detect archive type from URL path, filename, or content."""
    url_lower = url.lower()
    
    # First, check filename extension (most reliable)
    if url_lower.endswith('.zip'):
        return 'zip'
    elif url_lower.endswith('.deb'):
        return 'deb'
    elif url_lower.endswith('.appimage'):
        return 'appimage'
    elif url_lower.endswith('.tar.xz'):
        return 'tar.xz'
    elif url_lower.endswith('.tar.bz2'):
        return 'tar.bz2'
    elif url_lower.endswith('.tar.gz') or url_lower.endswith('.tgz'):
        return 'tar.gz'
    
    # If no extension, check URL path for hints
    # Common patterns: /deb/, /appimage/, /tar.gz/, etc.
    if '/deb/' in url_lower or url_lower.endswith('/deb'):
        return 'deb'
    elif '/appimage/' in url_lower or url_lower.endswith('/appimage'):
        return 'appimage'
    elif '/zip/' in url_lower or url_lower.endswith('/zip'):
        return 'zip'
    elif '/tar.xz/' in url_lower or url_lower.endswith('/tar.xz'):
        return 'tar.xz'
    elif '/tar.bz2/' in url_lower or url_lower.endswith('/tar.bz2'):
        return 'tar.bz2'
    elif '/tar.gz/' in url_lower or '/tgz/' in url_lower or url_lower.endswith('/tar.gz') or url_lower.endswith('/tgz'):
        return 'tar.gz'
    
    # Default to tar.gz (most common)
    return 'tar.gz'


def inspect_archive(url: str, archive_type: Optional[str] = None) -> Dict:
    """
    Inspect an archive: download, extract, and analyze structure.
    Returns analysis results.
    """
    if archive_type is None:
        archive_type = detect_archive_type(url)
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="void_inspect_"))
    archive_path = temp_dir / "archive"
    extract_dir = temp_dir / "extracted"
    
    try:
        # Download
        download_file(url, archive_path)
        
        # Extract
        print(f"Extracting {archive_type} archive...")
        try:
            extract_archive(archive_path, extract_dir, archive_type)
        except Exception as extract_error:
            # If extraction fails and type was auto-detected, suggest alternatives
            error_str = str(extract_error).lower()
            if archive_type == "tar.gz" and ("not a gzip" in error_str or "bad magic" in error_str):
                # Might be a deb file
                print(f"\n⚠ Warning: Extraction failed. The file might be a .deb archive.")
                print(f"   Try: ./void.py inspect {url} --type deb")
                raise Exception(f"Failed to extract as {archive_type}. File might be a different archive type. Try specifying --type deb")
            raise extract_error
        
        # Find root directory (often archives have a single root folder)
        entries = list(extract_dir.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            root_content = entries[0]
        else:
            root_content = extract_dir
        
        # Get directory tree
        tree = get_directory_tree(root_content, max_depth=3)
        
        # Find executables
        executables = find_executables(root_content, max_depth=5)
        
        # Calculate relative paths from extract_dir
        executable_paths = []
        for rel_path, metadata in executables[:20]:  # Top 20
            # If root_content is a subdirectory, adjust path
            if root_content != extract_dir:
                # Path relative to the single root folder
                full_path = root_content / rel_path
                rel_to_root = full_path.relative_to(root_content)
            else:
                rel_to_root = rel_path
            
            executable_paths.append({
                'path': str(rel_to_root),
                'score': metadata['score'],
                'is_executable': metadata['is_executable'],
                'size': metadata['size'],
                'parent': metadata['parent_dir'],
                'name': metadata.get('name', ''),
            })
        
        return {
            'url': url,
            'archive_type': archive_type,
            'extract_root': str(root_content.relative_to(extract_dir)) if root_content != extract_dir else ".",
            'directory_tree': tree,
            'executables': executable_paths,
            'temp_dir': temp_dir,  # Keep for cleanup
        }
    
    except Exception as e:
        # Cleanup on error
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise e


def cleanup_temp(temp_dir: Path) -> None:
    """Clean up temporary directory."""
    if temp_dir and temp_dir.exists():
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
