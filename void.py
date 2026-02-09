#!/usr/bin/env python3
from modules import installer, apps, tui, cleanup, inspector
import argparse
import sys
import os
import json
from pathlib import Path

# Add current directory to path so we can import modules
sys.path.append(str(Path(__file__).parent))


CONFIG_DIR = Path.home() / ".config" / "void"
CONFIG_FILE = CONFIG_DIR / "apps.json"
CUSTOM_APPS_FILE = CONFIG_DIR / "custom_apps.json"
BIN_DIR = Path.home() / "bin"


def check_path_warning():
    """Check if ~/bin is in PATH and warn if not."""
    path_env = os.environ.get("PATH", "")
    bin_str = str(BIN_DIR)
    if bin_str not in path_env:
        print("\n" + "="*60)
        print(" WARNING: ~/bin IS NOT IN YOUR PATH")
        print(" Apps installed by Void will not be found by your shell.")
        print(" Run this command to fix it:")
        print(f"    echo 'export PATH=\"$HOME/bin:$PATH\"' >> ~/.zshrc")
        print("    source ~/.zshrc")
        print("="*60 + "\n")
        return False
    return True


def load_config():
    if not CONFIG_FILE.exists():
        print(
            f"Config file not found at {CONFIG_FILE}. Run 'void init' first.")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def load_custom_apps():
    """Load and register custom apps from custom_apps.json."""
    if CUSTOM_APPS_FILE.exists():
        try:
            with open(CUSTOM_APPS_FILE, "r") as f:
                custom_apps = json.load(f)
                count = 0
                for key, data in custom_apps.items():
                    if key not in apps.SUPPORTED_APPS:
                        apps.SUPPORTED_APPS[key] = data
                        count += 1
                    else:
                        # Override existing? Let's say yes, custom overrides default
                        apps.SUPPORTED_APPS[key].update(data)
                        count += 1
                # Silent success or debug?
                # print(f"Loaded {count} custom app definitions.")
        except Exception as e:
            print(f"Warning: Failed to load custom_apps.json: {e}")


def cmd_init(args):
    """Initialize configuration and directories."""
    print("Initializing Void...")

    # Create config dir
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Create bin dir if it doesn't exist
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    # Create default config if missing
    if not CONFIG_FILE.exists():
        default_config = {
            "apps": ["vscode", "discord", "postman"]
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config at {CONFIG_FILE}")
    else:
        print(f"Config already exists at {CONFIG_FILE}")

    print("\nSetup complete! Add ~/bin to your PATH if it's not already there.")
    print("echo 'export PATH=\"$HOME/bin:$PATH\"' >> ~/.zshrc")


def cmd_list(args):
    """List supported and configured apps."""
    print("Supported applications:")
    for app_name in apps.SUPPORTED_APPS:
        print(f" - {app_name}")

    if CONFIG_FILE.exists():
        print("\nConfigured applications (in apps.json):")
        config = load_config()
        for app in config.get("apps", []):
            print(f" - {app}")


def cmd_install(args):
    """Install a specific application."""
    app_name = args.app_name
    if app_name not in apps.SUPPORTED_APPS:
        print(f"Error: Application '{app_name}' is not supported.")
        print("Use 'void list' to see available apps.")
        sys.exit(1)

    dry_run = getattr(args, 'dry_run', False)
    
    if dry_run:
        print(f"\n{'='*60}")
        print(f" DRY RUN: Installing {app_name}")
        print(f"{'='*60}\n")
        
        app_info = apps.SUPPORTED_APPS[app_name]
        app_install_dir = Path(f"/goinfre/{os.environ.get('USER', 'unknown')}/void/apps/{app_name}")
        
        print(f"App: {app_info['name']}")
        print(f"Type: {app_info['type']}")
        print(f"\nWould perform these actions:")
        print(f"  1. Download from: {app_info['url']}")
        print(f"  2. Extract to: {app_install_dir}")
        
        if app_info['type'] == 'appimage':
            binary_path = app_install_dir / "AppRun"
        else:
            binary_path = app_install_dir / app_info['bin_path']
        
        print(f"  3. Binary location: {binary_path}")
        print(f"  4. Create symlink: ~/bin/{app_info['link_name']} -> {binary_path}")
        
        if 'data_paths' in app_info:
            print(f"  5. Link data directories:")
            for data_path in app_info['data_paths']:
                print(f"     - ~/{data_path} -> /goinfre/$USER/void/data/{app_name}/{data_path}")
        
        if 'post_install' in app_info:
            print(f"  6. Run post-install scripts:")
            for idx, script in enumerate(app_info['post_install'], 1):
                print(f"     [{idx}] {script}")
        
        print(f"\n✓ Dry run complete. No changes made.")
        print(f"Run without --dry-run to actually install.\n")
        return
    
    installer.install_app(app_name)


def cmd_uninstall(args):
    """Uninstall a specific application."""
    app_name = args.app_name
    if app_name not in apps.SUPPORTED_APPS:
        print(f"Error: Application '{app_name}' is not supported.")
        return

    installer.uninstall_app(app_name)


def cmd_install_all(args):
    """Install all applications listed in config."""
    config = load_config()
    target_apps = config.get("apps", [])

    if not target_apps:
        print("No apps configured in apps.json.")
        return

    print(f"Installing {len(target_apps)} applications...")
    for app in target_apps:
        if app in apps.SUPPORTED_APPS:
            installer.install_app(app)
        else:
            print(
                f"Warning: Configured app '{app}' is not supported. Skipping.")


def cmd_entry(args):
    """Manually create a desktop entry with custom icon."""
    app_name = args.app
    icon_path = Path(args.icon)

    if app_name not in apps.SUPPORTED_APPS:
        print(f"Error: Application '{app_name}' is not supported.")
        return

    if not icon_path.exists():
        print(f"Error: Icon file not found at {icon_path}")
        return

    print(f"Creating desktop entry for {app_name} with icon {icon_path}...")
    app_info = apps.SUPPORTED_APPS[app_name]
    installer.create_desktop_entry(app_name, app_info, custom_icon=icon_path)


def cmd_refresh_icons(args):
    """Regenerate desktop entries for installed apps with improved icon detection."""
    app_name = getattr(args, "app_name", None)
    
    if app_name:
        # Refresh specific app
        if app_name not in apps.SUPPORTED_APPS:
            print(f"Error: Application '{app_name}' is not supported.")
            return
        
        if not installer.is_installed(app_name):
            print(f"Error: {app_name} is not installed.")
            return
        
        apps_to_refresh = [app_name]
    else:
        # Refresh all installed apps
        apps_to_refresh = installer.get_installed_app_names()
    
    if not apps_to_refresh:
        print("No installed apps found.")
        return
    
    print(f"\nRegenerating desktop entries for {len(apps_to_refresh)} app(s)...\n")
    
    for app in apps_to_refresh:
        app_info = apps.SUPPORTED_APPS.get(app)
        if not app_info:
            print(f"⚠ Skipping {app}: not in supported apps list")
            continue
        
        print(f"Refreshing {app}...")
        installer.create_desktop_entry(app, app_info)
    
    print(f"\n✓ Desktop entries refreshed successfully!")
    print("Icons should now appear in your application menu.")


def cmd_cleanup_analyze(args):
    """Analyze home directory and show cleanup opportunities."""
    print("\n" + "="*60)
    print(" Analyzing Home Directory Space Usage")
    print("="*60 + "\n")
    
    analysis = cleanup.analyze_home_space()
    disk_info = analysis['disk_info']
    
    # Show disk usage
    print(f"Disk Usage for {disk_info['path']}:")
    print(f"  Total: {cleanup.format_size(disk_info['total'])}")
    print(f"  Used:  {cleanup.format_size(disk_info['used'])} ({analysis['usage_percent']:.1f}%)")
    print(f"  Free:  {cleanup.format_size(disk_info['free'])}")
    print()
    
    # Show cleanup opportunities
    if analysis['cleanup_items']:
        print(f"Found {len(analysis['cleanup_items'])} items that can be cleaned:")
        print(f"  Total cleanable: {cleanup.format_size(analysis['total_cleanable'])}")
        print()
        
        # Group by category
        for category, items in analysis['by_category'].items():
            cat_size = sum(item.size for item in items)
            print(f"  {category}: {len(items)} items ({cleanup.format_size(cat_size)})")
            for item in sorted(items, key=lambda x: x.size, reverse=True)[:5]:  # Show top 5
                print(f"    - {item.path.relative_to(Path.home())}: {cleanup.format_size(item.size)}")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")
        print()
    else:
        print("No standard cleanup items found.")
    
    # Show large files
    print("\n" + "-"*60)
    print(" Large Files (>200MB) for Manual Review")
    print("-"*60)
    large_files = cleanup.find_large_files(min_size_mb=200, limit=10)
    if large_files:
        for file_path, size in large_files:
            try:
                rel_path = file_path.relative_to(Path.home())
            except ValueError:
                rel_path = file_path
            print(f"  {cleanup.format_size(size):>10} - {rel_path}")
    else:
        print("  No large files found.")
    
    # Show old downloads
    print("\n" + "-"*60)
    print(" Old Downloads (>90 days)")
    print("-"*60)
    old_downloads = cleanup.find_old_downloads(days_old=90)
    if old_downloads:
        total_old_size = sum(size for _, size, _ in old_downloads)
        print(f"  Found {len(old_downloads)} old files ({cleanup.format_size(total_old_size)})")
        for file_path, size, age in old_downloads[:10]:
            print(f"  {cleanup.format_size(size):>10} ({age:>3} days) - {file_path.name}")
        if len(old_downloads) > 10:
            print(f"  ... and {len(old_downloads) - 10} more")
    else:
        print("  No old downloads found.")
    
    print()
    if analysis['cleanup_items']:
        print("Run 'void cleanup --execute' to clean these files.")
    print()


def cmd_cleanup_execute(args):
    """Execute cleanup of safe-to-delete files."""
    print("\n" + "="*60)
    print(" Cleaning Home Directory")
    print("="*60 + "\n")
    
    analysis = cleanup.analyze_home_space()
    
    if not analysis['cleanup_items']:
        print("No cleanup opportunities found.")
        return
    
    print(f"Found {len(analysis['cleanup_items'])} items to clean.")
    print(f"Total size: {cleanup.format_size(analysis['total_cleanable'])}")
    print()
    
    # Show what will be cleaned
    print("Categories to clean:")
    for category, items in analysis['by_category'].items():
        cat_size = sum(item.size for item in items)
        print(f"  • {category}: {len(items)} items ({cleanup.format_size(cat_size)})")
    print()
    
    if not args.yes:
        response = input("Do you want to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cleanup cancelled.")
            return
    
    print("\nCleaning up...")
    
    # Get initial disk usage
    initial_disk = cleanup.get_disk_usage()
    total_freed = 0
    
    # 1. Clear entire .cache directory
    cache_freed = cleanup.clean_cache_directory(dry_run=False)
    if cache_freed > 0:
        print(f"[1/5] Cache directory: {cleanup.format_size(cache_freed)} freed")
        total_freed += cache_freed
    else:
        print(f"[1/5] Cache directory: already clean")
    
    # 2. Empty trash
    trash_freed = cleanup.clean_trash(dry_run=False)
    if trash_freed > 0:
        print(f"[2/5] Trash: {cleanup.format_size(trash_freed)} freed")
        total_freed += trash_freed
    else:
        print(f"[2/5] Trash: already clean")
    
    # 3. Deep VSCode cleanup
    vscode_freed = cleanup.clean_vscode_deep(dry_run=False)
    if vscode_freed > 0:
        print(f"[3/5] VSCode deep clean: {cleanup.format_size(vscode_freed)} freed")
        total_freed += vscode_freed
    else:
        print(f"[3/5] VSCode deep clean: already clean")
    
    # 4. Flatpak cleanup
    flatpak_freed = cleanup.clean_flatpak_cache(dry_run=False)
    if flatpak_freed > 0:
        print(f"[4/5] Flatpak cache: {cleanup.format_size(flatpak_freed)} freed")
        total_freed += flatpak_freed
    else:
        print(f"[4/5] Flatpak cache: already clean")
    
    # 5. Standard cleanup (build artifacts, etc.)
    items_cleaned, other_freed = cleanup.cleanup_items(analysis['cleanup_items'], dry_run=False)
    if other_freed > 0:
        print(f"[5/5] Build artifacts: {items_cleaned} items, {cleanup.format_size(other_freed)} freed")
        total_freed += other_freed
    else:
        print(f"[5/5] Build artifacts: already clean")
    
    print(f"\n✓ Total freed: {cleanup.format_size(total_freed)}")
    
    # Show updated disk usage
    final_disk = cleanup.get_disk_usage()
    print(f"\nDisk usage:")
    print(f"  Before: {cleanup.format_size(initial_disk['free'])} free")
    print(f"  After:  {cleanup.format_size(final_disk['free'])} free")
    print()



def cmd_inspect(args):
    """Inspect an archive to find the correct bin_path."""
    url = args.url
    archive_type = args.type
    
    print("\n" + "="*60)
    print(" Archive Inspector - Finding bin_path")
    print("="*60 + "\n")
    print("This tool will help you find the correct 'bin_path' for your app.")
    print("It downloads and extracts the archive to show its structure.\n")
    
    result = None
    try:
        result = inspector.inspect_archive(url, archive_type)
        
        print("\n" + "="*60)
        print(" Archive Structure Analysis")
        print("="*60 + "\n")
        
        print(f"Archive Type: {result['archive_type']}")
        if result['extract_root'] != ".":
            print(f"Root Directory: {result['extract_root']}")
        print()
        
        # Show directory tree
        print("Directory Structure:")
        print("-" * 60)
        for line in result['directory_tree'][:30]:  # Limit output
            print(line)
        if len(result['directory_tree']) > 30:
            print("... (showing first 30 items)")
        print()
        
        # Show potential executables
        if result['executables']:
            print("="*60)
            print(" Potential Binaries (sorted by relevance)")
            print("="*60 + "\n")
            
            for i, exe in enumerate(result['executables'][:10], 1):  # Top 10
                score_stars = "★" * min(exe['score'] // 3, 5)
                exec_marker = " [EXECUTABLE]" if exe['is_executable'] else ""
                size_mb = exe['size'] / (1024 * 1024) if exe['size'] > 0 else 0
                size_str = f" ({size_mb:.1f} MB)" if size_mb > 0 else ""
                
                print(f"{i}. {score_stars} {exe['path']}{exec_marker}{size_str}")
                print(f"   Score: {exe['score']}, Parent: {exe['parent']}")
                print()
            
            # Suggest the best one
            best = result['executables'][0]
            print("="*60)
            print(" RECOMMENDED bin_path:")
            print("="*60)
            print(f"\n  \"bin_path\": \"{best['path']}\"")
            print()
            
            if result['extract_root'] != ".":
                print(f"Note: Archive extracts to '{result['extract_root']}/' directory")
                print(f"      Your bin_path should be relative to that root.")
            print()
            
            print("If this doesn't look right, check the directory structure above")
            print("and choose the correct path to your executable.")
        else:
            print("⚠ No obvious binaries found.")
            print("Please check the directory structure above to find your executable.")
            print()
        
        print("="*60)
        print(" Example Configuration")
        print("="*60)
        print("\nBased on this analysis, your app entry might look like:")
        print()
        print(f'    "my-app": {{')
        print(f'        "name": "My App",')
        print(f'        "url": "{url}",')
        print(f'        "type": "{result["archive_type"]}",')
        if result['executables']:
            print(f'        "bin_path": "{result["executables"][0]["path"]}",')
        else:
            print(f'        "bin_path": "path/to/your/executable",  # FIXME: Find this!')
        print(f'        "link_name": "myapp"')
        print(f'    }}')
        print()
        
    except KeyboardInterrupt:
        print("\n\nInspection cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during inspection: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
    finally:
        # Cleanup
        if result and 'temp_dir' in result:
            print("\nCleaning up temporary files...")
            inspector.cleanup_temp(result['temp_dir'])
            print("Done.")


def cmd_health(args):
    """Check health of installed apps (bin symlinks, data symlinks)."""
    print("\n" + "="*60)
    print(" Installed Apps Health Check")
    print("="*60 + "\n")
    app_name = getattr(args, "app_name", None)
    if app_name:
        apps_to_check = [app_name]
        if app_name not in apps.SUPPORTED_APPS:
            print(f"Error: Unknown app '{app_name}'.")
            return
    else:
        apps_to_check = installer.get_installed_app_names()
    if not apps_to_check:
        print("No installed apps found.")
        return
    all_ok = True
    for app_name in apps_to_check:
        h = installer.check_app_health(app_name)
        status = "✓ OK" if h["ok"] else "✗ ISSUES"
        if not h["ok"]:
            all_ok = False
        print(f"  {app_name}: {status}")
        for issue in h["issues"]:
            print(f"    - {issue}")
    if not all_ok:
        print("\nRun './void.py repair' to fix symlinks (e.g. after migrating to a new post).")
    print()


def cmd_repair(args):
    """Re-establish symlinks for installed apps (use after migrating to a new post)."""
    print("\n" + "="*60)
    print(" Repair / Relink Installed Apps")
    print("="*60 + "\n")
    app_name = getattr(args, "app_name", None)
    if app_name:
        apps_to_repair = [app_name]
        if app_name not in apps.SUPPORTED_APPS:
            print(f"Error: Unknown app '{app_name}'.")
            return
    else:
        apps_to_repair = installer.get_installed_app_names()
    if not apps_to_repair:
        print("No installed apps to repair.")
        return
    repaired, failed = 0, []
    for app_name in apps_to_repair:
        try:
            if installer.repair_app(app_name):
                repaired += 1
        except Exception as e:
            failed.append((app_name, str(e)))
    print(f"\nRepaired {repaired} app(s).")
    if failed:
        print("Failed:")
        for app_name, err in failed:
            print(f"  - {app_name}: {err}")
    print()


def cmd_update(args):
    """Check for updates and optionally apply them."""
    print("\n" + "="*60)
    print(" Update Checker")
    print("="*60 + "\n")

    app_name = getattr(args, "app_name", None)
    if app_name:
        targets = [app_name]
    else:
        targets = installer.get_installed_app_names()

    if not targets:
        print("No installed apps found.")
        return

    results = []
    for name in targets:
        try:
            results.append(installer.check_update_for_app(name))
        except Exception as e:
            results.append({"app": name, "status": "error", "reason": str(e)})

    updates = [r for r in results if r.get("status") == "update_available"]
    uptodate = [r for r in results if r.get("status") == "up_to_date"]
    unknown = [r for r in results if r.get("status") in ("unknown", "not_installed", "error")]

    for r in results:
        status = r.get("status")
        if status == "update_available":
            fields = ", ".join(r.get("changed_fields", [])) or "metadata changed"
            print(f"  {r['app']}: ✨ update available ({fields})")
        elif status == "up_to_date":
            print(f"  {r['app']}: ✓ up to date")
        elif status == "not_installed":
            print(f"  {r['app']}: - not installed")
        elif status == "unknown":
            print(f"  {r['app']}: ? unknown ({r.get('reason','no metadata')})")
        else:
            print(f"  {r['app']}: ✗ error ({r.get('reason','')})")

    print()
    print(f"Summary: {len(updates)} update(s) available, {len(uptodate)} up-to-date, {len(unknown)} unknown/error.")

    if not args.apply:
        if updates:
            print("\nTo apply updates:")
            print("  ./void.py update --apply")
        return

    if not updates:
        print("\nNo updates to apply.")
        return

    print("\nApplying updates (reinstalling)...")
    for r in updates:
        name = r["app"]
        print(f"\n--- Updating {name} ---")
        try:
            installer.update_app(name)
        except Exception as e:
            print(f"Failed to update {name}: {e}")


def cmd_check_updates(args):
    """Check for updates for installed apps."""
    print("\n" + "="*60)
    print(" Checking for Updates")
    print("="*60 + "\n")
    
    installed = installer.get_installed_apps()
    
    if not installed:
        print("No installed apps found.")
        return
    
    updates_available = []
    up_to_date = []
    errors = []
    
    for app in installed:
        app_name = app['app_name']
        print(f"Checking {app['name']}...", end=" ")
        
        result = installer.check_app_update(app_name)
        
        if result['status'] == 'update_available':
            print(f"✓ Update available ({result['message']})")
            updates_available.append((app_name, app['name'], result))
        elif result['status'] == 'up_to_date':
            print("✓ Up to date")
            up_to_date.append(app_name)
        else:
            print(f"✗ {result['message']}")
            errors.append((app_name, result['message']))
    
    print("\n" + "="*60)
    print(f"Summary: {len(updates_available)} updates, {len(up_to_date)} up-to-date, {len(errors)} errors")
    
    if updates_available:
        print("\nUpdates available:")
        for app_name, name, result in updates_available:
            print(f"  • {name} ({app_name})")
        print(f"\nRun './void.py install <app_name>' to update")
    
    print()


def cmd_info(args):
    """Show detailed information about an app."""
    app_name = args.app_name
    
    print("\n" + "="*60)
    print(f" App Information: {app_name}")
    print("="*60 + "\n")
    
    info = installer.get_app_info(app_name)
    
    if not info:
        print(f"Error: Unknown app '{app_name}'")
        return
    
    if not info['installed']:
        print(f"Status: Not installed")
        print(f"Name: {info['app_info'].get('name')}")
        print(f"URL: {info['app_info'].get('url')}")
        print(f"Type: {info['app_info'].get('type')}")
        return
    
    # Format size
    size_mb = info['size'] / (1024 * 1024)
    
    print(f"Name: {info['name']}")
    print(f"Status: Installed")
    print(f"Size: {size_mb:.2f} MB")
    print(f"Install Directory: {info['install_dir']}")
    print(f"Binary: {info['binary_path']}")
    print(f"  Exists: {'✓' if info['binary_exists'] else '✗'}")
    print(f"Symlink: {info['link_path']}")
    print(f"  Exists: {'✓' if info['link_exists'] else '✗'}")
    
    if info['installed_at']:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(info['installed_at'])
            print(f"Installed: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            print(f"Installed: {info['installed_at']}")
    
    print(f"Type: {info['type']}")
    print(f"Source URL: {info['source_url']}")
    
    if info['data_paths']:
        print(f"\nData Paths:")
        for data in info['data_paths']:
            status = "✓ symlinked" if data['is_symlink'] else ("✓ exists" if data['exists'] else "✗ missing")
            print(f"  • {data['path']}: {status}")
    
    # Check for updates
    print(f"\nChecking for updates...", end=" ")
    update_result = installer.check_app_update(app_name)
    if update_result['status'] == 'update_available':
        print(f"✓ Update available ({update_result['message']})")
    elif update_result['status'] == 'up_to_date':
        print("✓ Up to date")
    else:
        print(f"✗ {update_result['message']}")
    
    print()


def cmd_reinstall(args):
    """Reinstall an application."""
    app_name = args.app_name
    
    if app_name not in apps.SUPPORTED_APPS:
        print(f"Error: Unknown app '{app_name}'")
        return
    
    print(f"\n{'='*60}")
    print(f" Reinstalling {app_name}")
    print(f"{'='*60}\n")
    
    # Check if installed
    app_dir = Path(f"/goinfre/{os.environ.get('USER', 'unknown')}/void/apps/{app_name}")
    
    if app_dir.exists():
        print(f"Uninstalling {app_name}...")
        installer.uninstall_app(app_name)
    else:
        print(f"{app_name} not currently installed")
    
    print(f"\nInstalling {app_name}...")
    installer.install_app(app_name)


def cmd_export(args):
    """Export list of installed apps."""
    installed = installer.get_installed_apps()
    
    if not installed:
        print("No installed apps found.")
        return
    
    export_data = {
        'version': '1.0',
        'exported_at': installer._now_iso(),
        'apps': [app['app_name'] for app in installed]
    }
    
    import json
    print(json.dumps(export_data, indent=2))


def cmd_import(args):
    """Import and install apps from exported list."""
    import json
    
    file_path = args.file
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file")
        return
    
    if 'apps' not in data:
        print("Error: Invalid export file (missing 'apps' field)")
        return
    
    apps_to_install = data['apps']
    
    print(f"\n{'='*60}")
    print(f" Importing {len(apps_to_install)} apps")
    print(f"{'='*60}\n")
    
    for app_name in apps_to_install:
        print(f"  • {app_name}")
    
    print()
    
    if not args.yes:
        response = input("Install these apps? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Import cancelled.")
            return
    
    print()
    success = 0
    failed = []
    
    for app_name in apps_to_install:
        if app_name not in apps.SUPPORTED_APPS:
            print(f"✗ {app_name}: Unknown app")
            failed.append(app_name)
            continue
        
        try:
            print(f"\nInstalling {app_name}...")
            installer.install_app(app_name)
            success += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            failed.append(app_name)
    
    print(f"\n{'='*60}")
    print(f"Import complete: {success} installed, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Void - 1337 School Storage Manager made by ['abdessel']")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init
    subparsers.add_parser("init", help="Initialize Void configuration")

    # List
    subparsers.add_parser("list", help="List supported and configured apps")

    # Install
    parser_install = subparsers.add_parser(
        "install", help="Install a specific application")
    parser_install.add_argument(
        "app_name", help="Name of the application to install")
    parser_install.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without actually doing it")

    # Uninstall
    parser_uninstall = subparsers.add_parser(
        "uninstall", help="Uninstall a specific application")
    parser_uninstall.add_argument(
        "app_name", help="Name of the application to uninstall")

    # Install All
    subparsers.add_parser("install-all", help="Install all apps from config")

    # Manual Entry
    parser_entry = subparsers.add_parser(
        "entry", help="Create/Update desktop entry")
    parser_entry.add_argument(
        "-a", "--app", required=True, help="Application name")
    parser_entry.add_argument(
        "-i", "--icon", required=True, help="Path to icon file")

    # Refresh Icons
    parser_refresh = subparsers.add_parser(
        "refresh-icons", help="Regenerate desktop entries with updated icon detection")
    parser_refresh.add_argument(
        "app_name", nargs="?", help="Specific app to refresh (default: all installed)")

    # TUI
    subparsers.add_parser("tui", help="Launch Text User Interface (Default)")

    # Cleanup
    parser_cleanup = subparsers.add_parser(
        "cleanup", help="Clean up safe-to-delete files from home directory")
    parser_cleanup.add_argument(
        "--execute", action="store_true", help="Execute cleanup (default: analyze only)")
    parser_cleanup.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # Inspect
    parser_inspect = subparsers.add_parser(
        "inspect", help="Inspect an archive to find the correct bin_path")
    parser_inspect.add_argument(
        "url", help="URL of the archive to inspect")
    parser_inspect.add_argument(
        "-t", "--type", help="Archive type (auto-detected if not specified)",
        choices=["tar.gz", "tar.xz", "tar.bz2", "zip", "deb", "appimage"])
    parser_inspect.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed error messages")

    # Health check
    parser_health = subparsers.add_parser(
        "health", help="Check health of installed apps (symlinks, data dirs)")
    parser_health.add_argument(
        "app_name", nargs="?", help="Check specific app (default: all installed)")

    # Repair / Relink
    parser_repair = subparsers.add_parser(
        "repair", help="Re-establish symlinks (run after migrating to a new post)")
    parser_repair.add_argument(
        "app_name", nargs="?", help="Repair specific app (default: all installed)")

    # Update checker
    parser_update = subparsers.add_parser(
        "update", help="Check for updates for installed apps")
    parser_update.add_argument(
        "app_name", nargs="?", help="Check/update a specific app (default: all installed)")
    parser_update.add_argument(
        "--apply", action="store_true", help="Reinstall apps that have updates available")
    
    # Check updates (simpler version)
    subparsers.add_parser(
        "check-updates", help="Check for updates for all installed apps")
    
    # App info
    parser_info = subparsers.add_parser(
        "info", help="Show detailed information about an app")
    parser_info.add_argument(
        "app_name", help="Name of the application")
    
    # Reinstall
    parser_reinstall = subparsers.add_parser(
        "reinstall", help="Reinstall an application (uninstall + install)")
    parser_reinstall.add_argument(
        "app_name", help="Name of the application to reinstall")
    
    # Export
    subparsers.add_parser(
        "export", help="Export list of installed apps to JSON")
    
    # Import
    parser_import = subparsers.add_parser(
        "import", help="Import and install apps from exported JSON")
    parser_import.add_argument(
        "file", help="Path to exported JSON file")
    parser_import.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # Load custom apps
    load_custom_apps()

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "install":
        cmd_install(args)
    elif args.command == "uninstall":
        cmd_uninstall(args)
    elif args.command == "install-all":
        cmd_install_all(args)
    elif args.command == "entry":
        cmd_entry(args)
    elif args.command == "refresh-icons":
        cmd_refresh_icons(args)
    elif args.command == "tui":
        tui.run()
    elif args.command == "cleanup":
        if args.execute:
            cmd_cleanup_execute(args)
        else:
            cmd_cleanup_analyze(args)
    elif args.command == "inspect":
        cmd_inspect(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "repair":
        cmd_repair(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "check-updates":
        cmd_check_updates(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "reinstall":
        cmd_reinstall(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "import":
        cmd_import(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "repair":
        cmd_repair(args)
    elif args.command == "update":
        cmd_update(args)
    else:
        # Default to TUI if no args, or help?
        # User requested tool to be a TUI tool. Defaulting to TUI is nice.
        # But let's check if sys.stdout is a tty.
        if sys.stdout.isatty():
            # Check PATH before launching TUI
            check_path_warning()  # CLI warning (might be overwritten by TUI init)
            # Pass path status to TUI?
            tui.run(missing_path=str(BIN_DIR)
                    not in os.environ.get("PATH", ""))
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
