
import unittest
import os
import shutil
import tempfile
from pathlib import Path
import sys
from unittest.mock import patch

# Add parent dir to path
sys.path.append(str(Path(__file__).parent.parent))

from modules import installer

class TestDataLinking(unittest.TestCase):
    def setUp(self):
        # Create temp dirs
        self.test_dir = tempfile.mkdtemp()
        self.fake_home = Path(self.test_dir) / "home"
        self.fake_home.mkdir()
        
        self.void_root = Path(self.test_dir) / "goinfre_void"
        self.void_data = self.void_root / "void" / "data"
        
        # Override constants
        # We need to patch Path.home() essentially, or carefully use os.environ['HOME'] if we used that?
        # In installer.py we used Path.home(). We need to patch it.
        pass
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('modules.installer.Path.home')
    def test_link_data_dirs_move_existing(self, mock_home):
        mock_home.return_value = self.fake_home
        
        # Setup: Create fake ~/.vscode with data
        vscode_dir = self.fake_home / ".vscode"
        vscode_dir.mkdir()
        with open(vscode_dir / "extension.txt", "w") as f:
            f.write("Important Data")
            
        # Override installer constants that depend on default HOME?
        # Actually installer defined constants at top level: BIN_DIR = Path.home() / "bin"
        # Since we import BEFORE patching, BIN_DIR is already set to real home. 
        # But link_data_dirs uses Path.home() inside the function loop?
        # "home_path = Path.home() / relative_path" -> YES.
        
        # Also need to override DATA_DIR since we changed VOID_ROOT
        installer.DATA_DIR = self.void_data
        
        app_name = "vscode"
        data_paths = [".vscode"]
        
        # Execute
        installer.link_data_dirs(app_name, data_paths)
        
        # Verify
        # 1. Symlink created
        self.assertTrue(vscode_dir.is_symlink())
        
        # 2. Target path
        # Implementation strips leading dots: ".vscode" -> "vscode"
        target_path = self.void_data / "vscode" / "vscode"
        self.assertEqual(vscode_dir.resolve(), target_path.resolve())
        
        # 3. Data preserved
        self.assertTrue((target_path / "extension.txt").exists())
        with open(target_path / "extension.txt", "r") as f:
            self.assertEqual(f.read(), "Important Data")

    @patch('modules.installer.Path.home')
    def test_link_data_dirs_create_new(self, mock_home):
        mock_home.return_value = self.fake_home
        
        installer.DATA_DIR = self.void_data
        
        # Setup: No directory exists at ~/.config/discord
        
        app_name = "discord"
        data_paths = [".config/discord"]
        
        # Execute
        installer.link_data_dirs(app_name, data_paths)
        
        # Verify
        home_path = self.fake_home / ".config/discord"
        # ".config/discord" -> replace -> ".config_discord" -> strip -> "config_discord"
        target_path = self.void_data / "discord" / "config_discord"
        
        self.assertTrue(home_path.is_symlink())
        self.assertTrue(target_path.exists())
        

if __name__ == '__main__':
    unittest.main()
