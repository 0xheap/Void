#!/usr/bin/env python3
"""
Test post-install script functionality
"""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.installer import run_post_install_scripts


class TestPostInstallScripts(unittest.TestCase):
    
    @patch('modules.installer.subprocess.run')
    @patch('modules.installer.apps.SUPPORTED_APPS', {
        'test-app': {
            'link_name': 'testapp'
        }
    })
    def test_placeholder_replacement(self, mock_run):
        """Test that placeholders are correctly replaced"""
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        
        binary_path = Path('/goinfre/user/void/apps/test-app/bin/app')
        scripts = [
            "{bin} --version",
            "{link} --help"
        ]
        
        run_post_install_scripts('test-app', scripts, binary_path)
        
        # Check that subprocess.run was called with replaced placeholders
        calls = mock_run.call_args_list
        self.assertEqual(len(calls), 2)
        
        # First call should have {bin} replaced
        self.assertIn('/goinfre/user/void/apps/test-app/bin/app --version', 
                     calls[0][0][0])
        
        # Second call should have {link} replaced
        self.assertIn('testapp --help', calls[1][0][0])
    
    @patch('modules.installer.subprocess.run')
    @patch('modules.installer.apps.SUPPORTED_APPS', {
        'test-app': {
            'link_name': 'testapp'
        }
    })
    def test_script_execution_success(self, mock_run):
        """Test successful script execution"""
        mock_run.return_value = MagicMock(
            returncode=0, 
            stdout='Success output', 
            stderr=''
        )
        
        binary_path = Path('/test/path')
        scripts = ["echo 'test'"]
        
        # Should not raise any exceptions
        run_post_install_scripts('test-app', scripts, binary_path)
        
        mock_run.assert_called_once()
    
    @patch('modules.installer.subprocess.run')
    @patch('modules.installer.apps.SUPPORTED_APPS', {
        'test-app': {
            'link_name': 'testapp'
        }
    })
    def test_script_execution_failure(self, mock_run):
        """Test that script failures are handled gracefully"""
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout='', 
            stderr='Error message'
        )
        
        binary_path = Path('/test/path')
        scripts = ["false"]
        
        # Should not raise exceptions, just print error
        run_post_install_scripts('test-app', scripts, binary_path)
        
        mock_run.assert_called_once()


if __name__ == '__main__':
    unittest.main()
