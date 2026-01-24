#!/usr/bin/env python3
from modules import installer, apps, tui
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
