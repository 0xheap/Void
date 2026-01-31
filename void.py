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
        print("Run 'void cleanup --execute' to clean these files.")
    else:
        print("No cleanup opportunities found. Your home directory is clean!")
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
    
    if not args.yes:
        response = input("Do you want to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cleanup cancelled.")
            return
    
    print("\nCleaning up...")
    items_cleaned, bytes_freed = cleanup.cleanup_items(analysis['cleanup_items'], dry_run=False)
    
    print(f"\n✓ Cleaned {items_cleaned} items")
    print(f"✓ Freed {cleanup.format_size(bytes_freed)}")
    
    # Show updated disk usage
    disk_info = cleanup.get_disk_usage()
    print(f"\nUpdated disk usage:")
    print(f"  Free: {cleanup.format_size(disk_info['free'])}")
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
        apps_to_check = installer.get_installed_apps()
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
        apps_to_repair = installer.get_installed_apps()
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
