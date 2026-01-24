from modules import installer
import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))


class TestDesktopEntries(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    @patch('modules.installer.DESKTOP_DIR')
    @patch('modules.installer.BIN_DIR')
    @patch('modules.installer.APPS_DIR')
    @patch('modules.installer.find_icon')
    def test_create_desktop_entry(self, mock_find_icon, mock_apps_dir, mock_bin_dir, mock_desktop_dir, mock_file_open):
        # Setup
        app_name = "test-app"
        app_info = {
            "name": "Test Application",
            "link_name": "test-app-bin"
        }

        # Mock Find Icon
        mock_find_icon.return_value = Path("/path/to/app/logo.png")

        # Mock Paths
        mock_bin_dir.__truediv__.return_value = Path(
            "/home/user/bin/test-app-bin")
        mock_desktop_dir.__truediv__.return_value = MagicMock()  # The output file
        mock_desktop_file = mock_desktop_dir.__truediv__.return_value

        # Execute
        installer.create_desktop_entry(app_name, app_info)

        # Verify file write
        mock_file_open.assert_called_once()
        handle = mock_file_open()

        # Check content
        args, _ = handle.write.call_args
        written_content = args[0]

        print(f"Written Desktop Entry:\n{written_content}")

        self.assertIn("Name=Test Application", written_content)
        self.assertIn("Exec=/home/user/bin/test-app-bin", written_content)
        self.assertIn("Icon=/path/to/app/logo.png", written_content)
        self.assertIn("Type=Application", written_content)

        # Verify permissions
        mock_desktop_file.chmod.assert_called_with(0o755)


if __name__ == "__main__":
    unittest.main()
