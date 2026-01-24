from modules import installer
import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))


class TestEntryPersistence(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    @patch('modules.installer.shutil.copy')
    @patch('modules.installer.DESKTOP_DIR')
    @patch('modules.installer.BIN_DIR')
    @patch('modules.installer.APPS_DIR')
    def test_custom_icon_copy(self, mock_apps_dir, mock_bin_dir, mock_desktop_dir, mock_copy, mock_file_open):
        # Setup
        app_name = "test-app"
        app_info = {
            "name": "Test Application",
            "link_name": "test-app-bin"
        }
        custom_icon_path = "/home/user/Downloads/cool_icon.png"

        # Mock Paths
        mock_bin_dir.__truediv__.return_value = Path(
            "/home/user/bin/test-app-bin")
        mock_desktop_dir.__truediv__.return_value = MagicMock()

        # Mock App Dir
        mock_app_install_dir = MagicMock()
        mock_apps_dir.__truediv__.return_value = mock_app_install_dir
        mock_app_install_dir.exists.return_value = True  # App exists

        # Setup target icon path
        # installer logic: target_icon = app_install_dir / f"custom_icon{source_icon.suffix}"
        # We need to ensure the mocks handle this division correctly to inspect it later
        mock_target_icon = MagicMock()
        mock_target_icon.__str__.return_value = "/goinfre/user/void/apps/test-app/custom_icon.png"

        mock_app_install_dir.__truediv__.side_effect = lambda x: mock_target_icon if "custom_icon" in str(
            x) else MagicMock()

        # Execute
        installer.create_desktop_entry(
            app_name, app_info, custom_icon=custom_icon_path)

        # Verify Copy
        # We expect shutil.copy(source, target)
        print("Verifying icon copy...")
        mock_copy.assert_called()
        args, _ = mock_copy.call_args
        source = args[0]
        target = args[1]

        self.assertEqual(str(source), str(
            Path(custom_icon_path).resolve()))  # Should resolve
        # The target should be derived from app_install_dir
        # Since we mocked __truediv__, we check if it matches our expectation or at least was called

        # Verify Content uses NEW path
        mock_file_open.assert_called_once()
        handle = mock_file_open()
        args, _ = handle.write.call_args
        written_content = args[0]

        print(f"Written Content:\n{written_content}")
        # The content should contain the path to the COPIED icon, not the original
        self.assertIn(
            "Icon=/goinfre/user/void/apps/test-app/custom_icon.png", written_content)


if __name__ == "__main__":
    unittest.main()
