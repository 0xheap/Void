import curses
import sys
import os
from pathlib import Path
from . import apps, installer

class VoidTUI:
    def __init__(self, stdscr, missing_path=False):
        self.stdscr = stdscr
        self.missing_path = missing_path
        self.apps_list = sorted(apps.SUPPORTED_APPS.keys())
        self.selected_indices = set()
        self.current_index = 0
        self.scroll_offset = 0
        
        # Color pairs
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # Selected row
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Installed
        curses.init_pair(3, curses.COLOR_CYAN, -1)   # Selected to install
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)   # Warning
        
        # Hide cursor
        curses.curs_set(0)

    def is_installed(self, app_name):
        app_dir = installer.APPS_DIR / app_name
        return app_dir.exists()

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # Title
        title = " Void - 42 School Storage Manager "
        self.stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.A_REVERSE)
        
        # PATH Warning
        list_start_y = 1
        if self.missing_path:
            warn_msg = " WARNING: ~/bin is NOT in your PATH. Apps won't run directly! "
            self.stdscr.addstr(1, (width - len(warn_msg)) // 2, warn_msg, curses.color_pair(4) | curses.A_BOLD)
            list_start_y = 2
        
        # Help text
        status_bar = " UP/DOWN: Navigate | SPACE: Toggle | ENTER: Install Selected | q: Quit "
        try:
            self.stdscr.addstr(height - 1, 0, status_bar[:width-1], curses.A_REVERSE)
        except curses.error:
            pass # Ignore if window too small
        
        # List area
        list_h = height - list_start_y - 1
        
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
            if idx == self.current_index:
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
        
        # Adjust list height logic for scroll
        height, _ = self.stdscr.getmaxyx()
        list_start_y = 2 if self.missing_path else 1
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
            app = self.apps_list[self.current_index]
            if app in self.selected_indices:
                self.selected_indices.remove(app)
            else:
                self.selected_indices.add(app)
        elif key == ord('\n') or key == curses.KEY_ENTER:
            if self.selected_indices:
                self.run_install()
                self.selected_indices.clear() # Clear selection after install
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
            
            win.addstr(2, 2, f"{action} {i+1}/{total}: {apps.SUPPORTED_APPS[app_name]['name']}")
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
                win.addstr(2, 2, f"ERROR installing {apps.SUPPORTED_APPS[app_name]['name']}:")
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

def run(missing_path=False):
    curses.wrapper(lambda stdscr: _run_loop(stdscr, missing_path))

def _run_loop(stdscr, missing_path):
    tui = VoidTUI(stdscr, missing_path)
    while True:
        tui.draw()
        if not tui.handle_input():
            break
