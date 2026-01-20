
import unittest
import os
import shutil
import tempfile
import tarfile
from pathlib import Path
import sys

# Add parent dir to path
sys.path.append(str(Path(__file__).parent.parent))

from modules import installer, apps

class TestInstaller(unittest.TestCase):
    def setUp(self):
        # Create temp dirs
        self.test_dir = tempfile.mkdtemp()
        self.void_root = Path(self.test_dir) / "goinfre_void"
        self.bin_dir = Path(self.test_dir) / "bin"
        
        # Override constants in installer
        installer.VOID_ROOT = self.void_root
        installer.APPS_DIR = self.void_root / "void" / "apps"
        installer.BIN_DIR = self.bin_dir
        
        # Mock app definition - Tarball
        apps.SUPPORTED_APPS["testapp"] = {
            "name": "Test App",
            "url": "file:///tmp/dummy.tar.gz",
            "type": "tar.gz",
            "bin_path": "TestApp/bin/run",
            "link_name": "test-run"
        }
        
        # Mock app definition - AppImage
        apps.SUPPORTED_APPS["testimage"] = {
            "name": "Test Image",
            "url": "file:///tmp/dummy.AppImage",
            "type": "appimage",
            "bin_path": "dummy.AppImage", # Filename kept
            "link_name": "test-image"
        }
        
        # Create a dummy tarball
        self.tar_path = Path(self.test_dir) / "testapp.tar.gz"
        self.create_dummy_tar(self.tar_path)
        
        # Create a dummy AppImage (just a text file)
        self.appimage_path = Path(self.test_dir) / "dummy.AppImage"
        with open(self.appimage_path, "w") as f:
            f.write("#!/bin/bash\necho 'I am an AppImage'")
            
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def create_dummy_tar(self, path):
        # Create a structure: TestApp/bin/run
        structure_dir = Path(self.test_dir) / "structure"
        bin_dir = structure_dir / "TestApp" / "bin"
        bin_dir.mkdir(parents=True)
        
        run_file = bin_dir / "run"
        with open(run_file, "w") as f:
            f.write("#!/bin/bash\necho 'Hello'")
        run_file.chmod(0o755)
        
        with tarfile.open(path, "w:gz") as tar:
            tar.add(structure_dir, arcname=".")
            
    def test_install_tar_flow(self):
        # Mock download
        original_download = installer.download_file
        installer.download_file = lambda url, target: shutil.copy(self.tar_path, target)
        
        try:
            installer.install_app("testapp")
            
            # Verify
            app_dir = installer.APPS_DIR / "testapp"
            self.assertTrue(app_dir.exists())
            installed_bin = app_dir / "TestApp/bin/run"
            self.assertTrue(installed_bin.exists())
            
            symlink = self.bin_dir / "test-run"
            self.assertTrue(symlink.exists())
            self.assertEqual(symlink.resolve(), installed_bin.resolve())
        finally:
            installer.download_file = original_download

    def test_install_appimage_flow(self):
        # Mock download
        original_download = installer.download_file
        installer.download_file = lambda url, target: shutil.copy(self.appimage_path, target)
        
        try:
            installer.install_app("testimage")
            
            # Verify
            app_dir = installer.APPS_DIR / "testimage"
            self.assertTrue(app_dir.exists())
            
            installed_bin = app_dir / "dummy.AppImage"
            self.assertTrue(installed_bin.exists())
            # Check executable
            self.assertTrue(os.access(installed_bin, os.X_OK))
            
            symlink = self.bin_dir / "test-image"
            self.assertTrue(symlink.exists())
            self.assertEqual(symlink.resolve(), installed_bin.resolve())
            
        finally:
            installer.download_file = original_download

if __name__ == '__main__':
    unittest.main()
