from modules import tui, apps
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add project root to path (needed if running directly, harmless if -m)
sys.path.append(str(Path(__file__).parent.parent))


class TestTUISearch(unittest.TestCase):
    @patch('modules.tui.curses')
    def test_search_filtering(self, mock_curses):
        # Setup mock stdscr
        stdscr = MagicMock()

        # Instantiate TUI
        # The patch ensures lookup of 'curses' inside 'modules.tui' gets our mock
        tui_instance = tui.VoidTUI(stdscr)

        # Test 1: Initial state (all apps)
        tui_instance.update_filter()
        self.assertEqual(len(tui_instance.apps_list), len(
            apps.SUPPORTED_APPS), "Should show all apps initially")

        # Test 2: Search for 'code'
        tui_instance.search_query = "code"
        tui_instance.update_filter()

        filtered = tui_instance.apps_list
        print(f"Searching 'code', found: {filtered}")
        self.assertIn("vscode", filtered)
        # self.assertIn("discord", filtered) # discord no longer matches "code" logic if strict, but 'disCORD' has 'c', 'o', 'd' ... but not substring "code"
        self.assertNotIn("neovim", filtered)

        # Test 3: Search for specific name 'blender'
        tui_instance.search_query = "blender"
        tui_instance.update_filter()
        self.assertIn("blender", tui_instance.apps_list)
        self.assertEqual(len(tui_instance.apps_list), 1)

        # Test 4: Search for something non-existent
        tui_instance.search_query = "xyz123"
        tui_instance.update_filter()
        self.assertEqual(len(tui_instance.apps_list), 0)

        # Test 5: Case insensitivity
        tui_instance.search_query = "VSCODE"
        tui_instance.update_filter()
        self.assertIn("vscode", tui_instance.apps_list)

        print("\nAll search logic tests passed!")


if __name__ == "__main__":
    unittest.main()
