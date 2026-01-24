from modules import installer, apps
import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))


class TestAppImageInstaller(unittest.TestCase):

    @patch('modules.installer.subprocess.run')
    @patch('modules.installer.shutil')
    @patch('modules.installer.urllib.request.urlopen')
    @patch('modules.installer.create_symlink')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_install_appimage_extraction(self, mock_print, mock_file_open, mock_symlink, mock_urlopen, mock_shutil, mock_subprocess):
        # Setup Method
        test_app = "test-appimage"
        apps.SUPPORTED_APPS[test_app] = {
            "name": "Test AppImage",
            "url": "http://example.com/test.AppImage",
            "type": "appimage",
            "bin_path": "ignored_for_extraction.AppImage",
            "link_name": "test-app"
        }

        # Mock Path operations to avoid real FS
        with patch('modules.installer.Path') as MockPath:
            # Setup paths
            mock_apps_dir = MagicMock()
            mock_install_dir = MagicMock()  # The app folder
            mock_temp_download = MagicMock()

            # Use real-ish path strings for debuggability if needed, but Mocks are fine
            mock_install_dir.__str__.return_value = "/mock/install/dir"
            mock_install_dir.resolve.return_value = MagicMock()
            mock_install_dir.resolve.return_value.__str__.return_value = "/mock/install/dir/resolved"

            # Configure resolving
            MockPath.return_value = mock_apps_dir
            installer.APPS_DIR = mock_apps_dir

            # When looking for app dir
            mock_apps_dir.__truediv__.side_effect = lambda x: mock_install_dir if x == test_app else mock_temp_download

            # Scenario: App NOT installed
            mock_install_dir.exists.return_value = False

            # Scenario: Extraction success
            mock_extracted_root = MagicMock()
            mock_extracted_root.exists.return_value = True
            mock_extracted_root.iterdir.return_value = []

            mock_install_dir.__truediv__.side_effect = lambda x: \
                mock_extracted_root if x == "squashfs-root" else \
                (MagicMock() if x == "temp.AppImage" else MagicMock())  # default mocks

            # Run install
            installer.install_app(test_app)

            # Verify subprocess called with --appimage-extract
            args, kwargs = mock_subprocess.call_args
            cmd_list = args[0]

            # cmd_list[0] will be a string of resolved path
            # cmd_list[1] should be --appimage-extract
            self.assertIn("--appimage-extract", cmd_list)
            self.assertEqual(kwargs['cwd'], mock_install_dir)

            # Verify symlink called with AppRun
            mock_symlink.assert_called_once()
            # If we want to be pedantic, we can check that it didn't crash.


if __name__ == "__main__":
    unittest.main()
