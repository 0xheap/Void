"""
Cleanup module for Void - Helps free space in home directory.
Identifies and removes safe-to-delete files (cache, logs, temporary files, etc.)
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class CleanupItem:
    """Represents an item that can be cleaned."""
    path: Path
    size: int
    category: str
    description: str
    safe: bool = True  # Whether it's safe to delete


def get_directory_size(path: Path) -> int:
    """Calculate total size of a directory in bytes."""
    total = 0
    try:
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            for entry in path.rglob('*'):
                try:
                    if entry.is_file():
                        total += entry.stat().st_size
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_disk_usage(path: Path = None) -> Dict[str, int]:
    """Get disk usage statistics for a path."""
    if path is None:
        path = Path.home()
    
    stat = shutil.disk_usage(path)
    return {
        'total': stat.total,
        'used': stat.used,
        'free': stat.free,
        'path': str(path)
    }


# Common cache and temporary directories to clean
CACHE_PATTERNS = [
    # Browser caches
    (".cache/mozilla", "Browser Cache", "Firefox cache files"),
    (".cache/google-chrome", "Browser Cache", "Chrome cache files"),
    (".cache/chromium", "Browser Cache", "Chromium cache files"),
    (".cache/brave", "Browser Cache", "Brave browser cache"),
    (".cache/librewolf", "Browser Cache", "LibreWolf cache"),
    
    # Application caches
    (".cache/pip", "Python Cache", "pip cache directory"),
    (".cache/pipenv", "Python Cache", "pipenv cache"),
    (".cache/npm", "Node Cache", "npm cache directory"),
    (".cache/yarn", "Node Cache", "yarn cache directory"),
    (".cache/cargo", "Rust Cache", "Cargo build cache"),
    (".cache/go-build", "Go Cache", "Go build cache"),
    
    # IDE/Editor caches
    (".cache/vscode", "IDE Cache", "VSCode cache"),
    (".cache/Code", "IDE Cache", "VSCode cache (alternative)"),
    (".cache/JetBrains", "IDE Cache", "JetBrains IDEs cache"),
    (".cache/sublime-text", "IDE Cache", "Sublime Text cache"),
    
    # System caches
    (".cache/thumbnails", "System Cache", "Thumbnail cache"),
    (".cache/fontconfig", "System Cache", "Font configuration cache"),
    
    # Temporary files
    (".local/share/Trash", "Trash", "Trash/Recycle bin contents"),
    (".tmp", "Temporary", "Temporary files directory"),
    ("tmp", "Temporary", "Temporary files in home"),
    
    # Build artifacts and compiled files
    ("__pycache__", "Build Artifacts", "Python bytecode cache"),
    ("*.pyc", "Build Artifacts", "Python compiled files"),
    (".pytest_cache", "Build Artifacts", "pytest cache"),
    ("node_modules", "Build Artifacts", "Node.js dependencies (if not needed)"),
    ("target", "Build Artifacts", "Rust build artifacts"),
    ("dist", "Build Artifacts", "Distribution/build directories"),
    ("build", "Build Artifacts", "Build directories"),
    (".gradle", "Build Artifacts", "Gradle cache"),
    (".m2", "Build Artifacts", "Maven cache"),
    
    # Log files
    ("*.log", "Logs", "Log files"),
    (".local/share/logs", "Logs", "Application logs"),
    
    # Old downloads (be careful with this)
    ("Downloads/*.deb", "Downloads", "Old .deb packages"),
    ("Downloads/*.tar.gz", "Downloads", "Old archives"),
    ("Downloads/*.zip", "Downloads", "Old zip files"),
    ("Downloads/*.AppImage", "Downloads", "Old AppImages"),
    
    # Package manager caches
    (".cache/pacman", "Package Cache", "Pacman cache"),
    (".cache/apt", "Package Cache", "APT cache"),
]


def find_cleanup_items(home_dir: Path = None) -> List[CleanupItem]:
    """Scan home directory and find items that can be cleaned."""
    if home_dir is None:
        home_dir = Path.home()
    
    items = []
    
    # Process each pattern
    for pattern, category, description in CACHE_PATTERNS:
        # Handle glob patterns
        if '*' in pattern:
            # Find all matching files/dirs
            if pattern.startswith('.'):
                search_path = home_dir / pattern
            else:
                search_path = home_dir / pattern
            
            # Use glob to find matches
            try:
                matches = list(home_dir.glob(pattern))
                for match in matches:
                    if match.exists():
                        size = get_directory_size(match)
                        if size > 0:
                            items.append(CleanupItem(
                                path=match,
                                size=size,
                                category=category,
                                description=description,
                                safe=True
                            ))
            except Exception:
                continue
        else:
            # Direct path
            target_path = home_dir / pattern.lstrip('/')
            if target_path.exists():
                size = get_directory_size(target_path)
                if size > 0:
                    items.append(CleanupItem(
                        path=target_path,
                        size=size,
                        category=category,
                        description=description,
                        safe=True
                    ))
    
    # Also scan for common patterns recursively (but limit depth)
    common_patterns = [
        ('__pycache__', 'Build Artifacts', 'Python bytecode cache'),
        ('*.pyc', 'Build Artifacts', 'Python compiled files'),
        ('node_modules', 'Build Artifacts', 'Node.js dependencies'),
        ('.pytest_cache', 'Build Artifacts', 'pytest cache'),
    ]
    
    # Limit recursive search to avoid scanning entire filesystem
    max_depth = 3
    for root, dirs, files in os.walk(home_dir):
        depth = len(Path(root).relative_to(home_dir).parts)
        if depth > max_depth:
            dirs[:] = []  # Don't recurse deeper
            continue
        
        # Check for __pycache__ directories
        if '__pycache__' in dirs:
            pycache_path = Path(root) / '__pycache__'
            size = get_directory_size(pycache_path)
            if size > 0:
                items.append(CleanupItem(
                    path=pycache_path,
                    size=size,
                    category='Build Artifacts',
                    description='Python bytecode cache',
                    safe=True
                ))
        
        # Check for .pytest_cache
        if '.pytest_cache' in dirs:
            pytest_path = Path(root) / '.pytest_cache'
            size = get_directory_size(pytest_path)
            if size > 0:
                items.append(CleanupItem(
                    path=pytest_path,
                    size=size,
                    category='Build Artifacts',
                    description='pytest cache',
                    safe=True
                ))
        
        # Check for node_modules (but be careful - ask user)
        if 'node_modules' in dirs:
            node_path = Path(root) / 'node_modules'
            size = get_directory_size(node_path)
            if size > 0:
                items.append(CleanupItem(
                    path=node_path,
                    size=size,
                    category='Build Artifacts',
                    description='Node.js dependencies (can be reinstalled)',
                    safe=True  # Safe but might need reinstall
                ))
    
    # Remove duplicates (same path)
    seen = set()
    unique_items = []
    for item in items:
        if str(item.path) not in seen:
            seen.add(str(item.path))
            unique_items.append(item)
    
    return unique_items


def cleanup_items(items: List[CleanupItem], dry_run: bool = False) -> Tuple[int, int]:
    """
    Clean up the specified items.
    Returns: (items_cleaned, bytes_freed)
    """
    total_freed = 0
    items_cleaned = 0
    
    for item in items:
        if not item.safe:
            continue
        
        try:
            if item.path.exists():
                size = get_directory_size(item.path)
                
                if not dry_run:
                    if item.path.is_file():
                        item.path.unlink()
                    elif item.path.is_dir():
                        shutil.rmtree(item.path)
                
                total_freed += size
                items_cleaned += 1
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not remove {item.path}: {e}")
            continue
    
    return items_cleaned, total_freed


def analyze_home_space() -> Dict:
    """Analyze home directory space usage and cleanup opportunities."""
    home_dir = Path.home()
    disk_info = get_disk_usage(home_dir)
    cleanup_items_list = find_cleanup_items(home_dir)
    
    total_cleanable = sum(item.size for item in cleanup_items_list)
    
    # Group by category
    by_category = {}
    for item in cleanup_items_list:
        if item.category not in by_category:
            by_category[item.category] = []
        by_category[item.category].append(item)
    
    return {
        'disk_info': disk_info,
        'cleanup_items': cleanup_items_list,
        'total_cleanable': total_cleanable,
        'by_category': by_category,
        'usage_percent': (disk_info['used'] / disk_info['total']) * 100 if disk_info['total'] > 0 else 0
    }
