import curses
import sys
import os
from pathlib import Path
from . import apps, installer, cleanup


class VoidTUI:
    def __init__(self, stdscr, missing_path=False):
        self.stdscr = stdscr
        self.missing_path = missing_path
        self.all_apps = sorted(apps.SUPPORTED_APPS.keys())
        self.apps_list = self.all_apps  # Currently displayed list
        self.selected_indices = set()
        self.current_index = 0
        self.scroll_offset = 0

        # Search state
        self.search_mode = False
        self.search_query = ""

        # Color pairs
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK,
                         curses.COLOR_WHITE)  # Selected row
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Installed
        curses.init_pair(3, curses.COLOR_CYAN, -1)   # Selected to install
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)   # Warning
        curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Search text

        # Hide cursor
        curses.curs_set(0)

    def is_installed(self, app_name):
        app_dir = installer.APPS_DIR / app_name
        return app_dir.exists()

    def update_filter(self):
        """Update apps_list based on search query"""
        if not self.search_query:
            self.apps_list = self.all_apps
        else:
            query = self.search_query.lower()
            self.apps_list = [
                app for app in self.all_apps
                if query in app.lower() or query in apps.SUPPORTED_APPS[app]["name"].lower()
            ]

        # Reset navigation if list changed/shrunk
        if self.current_index >= len(self.apps_list):
            self.current_index = max(0, len(self.apps_list) - 1)
        self.scroll_offset = 0  # simple reset to top on search change

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Title
        title = " Void - 1337 School Storage Manager "
        self.stdscr.addstr(0, (width - len(title)) // 2,
                           title, curses.A_BOLD | curses.A_REVERSE)

        # PATH Warning
        list_start_y = 1
        if self.missing_path:
            warn_msg = " WARNING: ~/bin is NOT in your PATH. Apps won't run directly! "
            self.stdscr.addstr(1, (width - len(warn_msg)) // 2,
                               warn_msg, curses.color_pair(4) | curses.A_BOLD)
            list_start_y = 2

        # Search Bar
        if self.search_mode or self.search_query:
            search_str = f" Search: {self.search_query}"
            if self.search_mode:
                search_str += "█"  # cursor block
            self.stdscr.addstr(list_start_y, 1, search_str,
                               curses.color_pair(5) | curses.A_BOLD)
            list_start_y += 1

        # Help text
        if self.search_mode:
            status_bar = " TYPE to search | ENTER: Done | ESC: Cancel "
        else:
            status_bar = f" UP/DOWN: Navigate | SPACE: Toggle | /: Search | ENTER: Install ({len(self.selected_indices)}) | c: Cleanup | q: Quit "

        try:
            self.stdscr.addstr(
                height - 1, 0, status_bar[:width-1], curses.A_REVERSE)
        except curses.error:
            pass  # Ignore if window too small

        # List area
        list_h = height - list_start_y - 1

        if not self.apps_list:
            self.stdscr.addstr(list_start_y + 1, 2,
                               "No apps found matching query.")

        for i in range(list_h):
            idx = i + self.scroll_offset
            if idx >= len(self.apps_list):
                break

            app_key = self.apps_list[idx]
            app_info = apps.SUPPORTED_APPS[app_key]

            # Status Indicators
            installed = self.is_installed(app_key)
            selected = app_key in self.selected_indices

            prefix = "[ ]"
            attr = curses.A_NORMAL

            if installed:
                prefix = "[I]"
                attr = curses.color_pair(2)
            if selected:
                prefix = "[*]"
                attr = curses.color_pair(3) | curses.A_BOLD

            # Highlight current row
            row_attr = attr
            if idx == self.current_index and not self.search_mode:
                row_attr = curses.color_pair(1)

            display_name = f"{prefix} {app_info['name']} ({app_key})"

            # Truncate
            if len(display_name) > width - 2:
                display_name = display_name[:width-5] + "..."

            try:
                self.stdscr.addstr(i + list_start_y, 1, display_name, row_attr)
            except curses.error:
                pass

        self.stdscr.refresh()

    def handle_input(self):
        key = self.stdscr.getch()

        if self.search_mode:
            # Search Input Handling
            if key == 27:  # ESC
                self.search_mode = False
                # Optional: clear query on cancel? Or keep it? keeping is usually friendlier
                # self.search_query = ""
                # self.update_filter()
            elif key == ord('\n') or key == curses.KEY_ENTER:
                self.search_mode = False
            elif key == curses.KEY_BACKSPACE or key == 127:
                if len(self.search_query) > 0:
                    self.search_query = self.search_query[:-1]
                    self.update_filter()
            elif 32 <= key <= 126:  # Printable chars
                self.search_query += chr(key)
                self.update_filter()
            return True

        # Normal Navigation Logic
        height, _ = self.stdscr.getmaxyx()

        # Calculate list height dynamically again (code duplication to be cleaned up later)
        list_start_y = 1
        if self.missing_path:
            list_start_y += 1
        if self.search_query:
            list_start_y += 1  # Search bar room

        list_h = height - list_start_y - 1

        if key == curses.KEY_UP and self.current_index > 0:
            self.current_index -= 1
            if self.current_index < self.scroll_offset:
                self.scroll_offset -= 1
        elif key == curses.KEY_DOWN and self.current_index < len(self.apps_list) - 1:
            self.current_index += 1
            if self.current_index >= self.scroll_offset + list_h:
                self.scroll_offset += 1
        elif key == ord(' '):
            if self.apps_list:
                app = self.apps_list[self.current_index]
                if app in self.selected_indices:
                    self.selected_indices.remove(app)
                else:
                    self.selected_indices.add(app)
        elif key == ord('/') or key == ord('s'):
            self.search_mode = True
        elif key == 27:  # ESC to clear search if not in search mode
            if self.search_query:
                self.search_query = ""
                self.update_filter()
        elif key == ord('\n') or key == curses.KEY_ENTER:
            if self.selected_indices:
                self.run_install()
                self.selected_indices.clear()  # Clear selection after install
        elif key == ord('c'):
            self.run_cleanup()
        elif key == ord('q'):
            return False

        return True

    def run_install(self):
        # Exit curses mode nicely essentially, or draw a progress window.
        # Simple approach: standard print is hijacked by curses.
        # We can suspend curses or just use a simple modal.

        # We'll use a simple blocking render for now.
        height, width = self.stdscr.getmaxyx()
        win = curses.newwin(height - 4, width - 4, 2, 2)
        win.box()
        win.refresh()

        total = len(self.selected_indices)
        for i, app_name in enumerate(self.selected_indices):
            win.clear()
            win.box()

            # Determine action
            installed = self.is_installed(app_name)
            action = "Uninstalling" if installed else "Installing"

            win.addstr(
                2, 2, f"{action} {i+1}/{total}: {apps.SUPPORTED_APPS[app_name]['name']}")
            win.addstr(4, 2, "Please wait... (Check stdout logs if needed)")
            win.refresh()

            try:
                # Basic suppression
                with open(os.devnull, 'w') as fnull:
                    # Save originals
                    old_stdout = sys.stdout
                    sys.stdout = fnull

                    try:
                        if installed:
                            installer.uninstall_app(app_name)
                        else:
                            installer.install_app(app_name)
                    finally:
                        sys.stdout = old_stdout
            except Exception as e:
                # Show error dialog
                win.clear()
                win.box()
                win.addstr(
                    2, 2, f"ERROR installing {apps.SUPPORTED_APPS[app_name]['name']}:")
                error_msg = str(e)
                # split long error
                if len(error_msg) > width - 6:
                    win.addstr(3, 2, error_msg[:width-6])
                    win.addstr(4, 2, error_msg[width-6:2*width-12])
                else:
                    win.addstr(3, 2, error_msg)

                win.addstr(height-6, 2, "Press any key to skip/continue...")
                win.refresh()
                win.getch()

        win.clear()
        win.box()
        win.addstr(2, 2, "Batch processing complete!")
        win.addstr(4, 2, "Press any key to return to menu.")
        win.refresh()
        win.getch()

    def run_cleanup(self):
        """Show cleanup analysis and allow user to clean."""
        height, width = self.stdscr.getmaxyx()
        win = curses.newwin(height - 4, width - 4, 2, 2)
        win.box()
        
        win.addstr(1, 2, "Analyzing home directory...")
        win.refresh()
        
        try:
            # Analyze cleanup opportunities
            analysis = cleanup.analyze_home_space()
            disk_info = analysis['disk_info']
            
            win.clear()
            win.box()
            
            # Show disk usage
            y = 1
            win.addstr(y, 2, f"Disk Usage: {disk_info['path']}", curses.A_BOLD)
            y += 1
            win.addstr(y, 4, f"Total: {cleanup.format_size(disk_info['total'])}")
            y += 1
            win.addstr(y, 4, f"Used:  {cleanup.format_size(disk_info['used'])} ({analysis['usage_percent']:.1f}%)")
            y += 1
            win.addstr(y, 4, f"Free:  {cleanup.format_size(disk_info['free'])}")
            y += 2
            
            if analysis['cleanup_items']:
                win.addstr(y, 2, f"Found {len(analysis['cleanup_items'])} items to clean:", curses.A_BOLD)
                y += 1
                win.addstr(y, 4, f"Total cleanable: {cleanup.format_size(analysis['total_cleanable'])}")
                y += 2
                
                # Show top categories
                win.addstr(y, 2, "Top categories:", curses.A_BOLD)
                y += 1
                for category, items in list(analysis['by_category'].items())[:5]:
                    cat_size = sum(item.size for item in items)
                    win.addstr(y, 4, f"{category}: {len(items)} items ({cleanup.format_size(cat_size)})")
                    y += 1
                    if y >= height - 8:
                        break
                
                y += 1
                win.addstr(y, 2, "Press 'y' to clean, any other key to cancel")
            else:
                win.addstr(y, 2, "No cleanup opportunities found. Your home is clean!")
                y += 2
                win.addstr(y, 2, "Press any key to continue")
            
            win.refresh()
            key = win.getch()
            
            if key == ord('y') and analysis['cleanup_items']:
                # Execute cleanup
                win.clear()
                win.box()
                win.addstr(2, 2, "Cleaning up... Please wait...")
                win.refresh()
                
                items_cleaned, bytes_freed = cleanup.cleanup_items(
                    analysis['cleanup_items'], dry_run=False)
                
                win.clear()
                win.box()
                win.addstr(2, 2, f"✓ Cleaned {items_cleaned} items", curses.color_pair(2))
                win.addstr(3, 2, f"✓ Freed {cleanup.format_size(bytes_freed)}")
                
                # Show updated disk usage
                disk_info = cleanup.get_disk_usage()
                win.addstr(5, 2, f"Updated free space: {cleanup.format_size(disk_info['free'])}")
                win.addstr(7, 2, "Press any key to continue")
                win.refresh()
                win.getch()
        except Exception as e:
            win.clear()
            win.box()
            win.addstr(2, 2, f"Error: {str(e)}")
            win.addstr(4, 2, "Press any key to continue")
            win.refresh()
            win.getch()


def run(missing_path=False):
    curses.wrapper(lambda stdscr: _run_loop(stdscr, missing_path))


def _run_loop(stdscr, missing_path):
    tui = VoidTUI(stdscr, missing_path)
    while True:
        tui.draw()
        if not tui.handle_input():
            break
