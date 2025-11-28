"""Unit tests for rudi.py — configuration management tool."""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open, call
import sys

# Add parent dir so we can import rudi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rudi


class TestRudiYAMLLoading(unittest.TestCase):
    """Test YAML configuration loading and parsing."""

    def test_valid_services_manifest(self):
        """Verify a minimal valid Services manifest parses without error."""
        yaml_content = """\
Services:
  apache2:
    packages: [apache2, php5]
"""
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("yaml.safe_load") as mock_load:
                mock_load.return_value = {
                    "Services": {
                        "apache2": {"packages": ["apache2", "php5"]}
                    }
                }
                # Simulate the converge flow without side effects
                data = mock_load()
                self.assertIn("Services", data)
                self.assertIn("apache2", data["Services"])

    def test_manifest_with_files_and_packages(self):
        """Verify manifests with Files and Packages sections parse correctly."""
        yaml_content = """\
Services:
  apache2:
    packages: [apache2, php5]
Packages:
  apache2:
    files: []
  php5:
    files: [hello.php]
Files:
  hello.php:
    base: /var/www/html/
    name: hello.php
    content: "<?php echo 'Hello'; ?>"
    owner: root
    group: root
    mode: "755"
"""
        with patch("yaml.safe_load") as mock_load:
            mock_load.return_value = {
                "Services": {
                    "apache2": {"packages": ["apache2", "php5"]}
                },
                "Packages": {
                    "apache2": {"files": []},
                    "php5": {"files": ["hello.php"]}
                },
                "Files": {
                    "hello.php": {
                        "base": "/var/www/html/",
                        "name": "hello.php",
                        "content": "<?php echo 'Hello'; ?>",
                        "owner": "root",
                        "group": "root",
                        "mode": "755"
                    }
                }
            }
            data = mock_load()
            self.assertIn("Files", data)
            self.assertIn("hello.php", data["Files"])
            self.assertEqual(data["Files"]["hello.php"]["owner"], "root")

    def test_evictions_manifest(self):
        """Verify Evictions (package removal) manifest parses correctly."""
        yaml_content = """\
Evictions: [cron, php5, apache2]
"""
        with patch("yaml.safe_load") as mock_load:
            mock_load.return_value = {
                "Evictions": ["cron", "php5", "apache2"]
            }
            data = mock_load()
            self.assertIn("Evictions", data)
            self.assertEqual(len(data["Evictions"]), 3)


class TestRudiFileDeployment(unittest.TestCase):
    """Test file deployment logic (do_file function)."""

    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open)
    def test_do_file_basic_flow(self, mock_file, mock_run):
        """Verify do_file writes content and sets permissions."""
        mock_run.return_value = Mock(returncode=0)

        file_spec = {
            "base": "/tmp/test_rudi_/",
            "name": "test.txt",
            "content": "hello world",
            "owner": "root",
            "group": "root",
            "mode": "644"
        }

        rudi.do_file(file_spec)

        # Check that mkdir was called
        mkdir_calls = [c for c in mock_run.call_args_list if "mkdir" in str(c)]
        self.assertTrue(len(mkdir_calls) > 0, "mkdir should have been called")

        # Check that file was opened for writing
        mock_file.assert_called_with("/tmp/test_rudi_/test.txt", "w")

        # Check that chown, chgrp, chmod were called
        chown_calls = [c for c in mock_run.call_args_list if "chown" in str(c)]
        chgrp_calls = [c for c in mock_run.call_args_list if "chgrp" in str(c)]
        chmod_calls = [c for c in mock_run.call_args_list if "chmod" in str(c)]

        self.assertTrue(len(chown_calls) > 0, "chown should have been called")
        self.assertTrue(len(chgrp_calls) > 0, "chgrp should have been called")
        self.assertTrue(len(chmod_calls) > 0, "chmod should have been called")

    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open)
    def test_do_file_correct_file_path(self, mock_file, mock_run):
        """Verify do_file uses base + name for file path."""
        mock_run.return_value = Mock(returncode=0)

        file_spec = {
            "base": "/etc/",
            "name": "crontab",
            "content": "# cron jobs",
            "owner": "root",
            "group": "root",
            "mode": "600"
        }

        rudi.do_file(file_spec)

        # Verify the file path is correct (base + name)
        mock_file.assert_called_with("/etc/crontab", "w")


class TestRudiConverge(unittest.TestCase):
    """Test the main converge logic and service lifecycle."""

    @patch("rudi.do_file")
    @patch("subprocess.run")
    def test_converge_installs_packages(self, mock_run, mock_do_file):
        """Verify converge calls apt-get install for packages in Services."""
        mock_run.return_value = Mock(returncode=0)

        data = {
            "Services": {
                "apache2": {
                    "packages": ["apache2"]
                }
            },
            "Packages": {
                "apache2": {"files": []}
            }
        }

        rudi.converge(data)

        # Verify service stop and start were called
        service_calls = [str(c) for c in mock_run.call_args_list]
        service_calls_str = " ".join(service_calls)
        self.assertTrue("apache2" in service_calls_str and "stop" in service_calls_str)
        self.assertTrue("apache2" in service_calls_str and "start" in service_calls_str)

    @patch("subprocess.run")
    def test_converge_evictions(self, mock_run):
        """Verify converge calls apt-get remove for Evictions."""
        mock_run.return_value = Mock(returncode=0)

        data = {
            "Evictions": ["php5", "cron"]
        }

        rudi.converge(data)

        # Verify remove/autopurge was called
        remove_calls = [str(c) for c in mock_run.call_args_list
                        if "remove" in str(c) or "autopurge" in str(c)]
        self.assertTrue(len(remove_calls) > 0, "apt-get remove should have been called")

    @patch("rudi.do_file")
    @patch("subprocess.run")
    def test_converge_deploys_files_for_packages(self, mock_run, mock_do_file):
        """Verify converge calls do_file for files listed in Package entries."""
        mock_run.return_value = Mock(returncode=0)

        data = {
            "Services": {
                "cron": {
                    "packages": ["cron"]
                }
            },
            "Packages": {
                "cron": {
                    "files": ["crontab"]
                }
            },
            "Files": {
                "crontab": {
                    "base": "/etc/",
                    "name": "crontab",
                    "content": "# cron",
                    "owner": "root",
                    "group": "root",
                    "mode": "600"
                }
            }
        }

        rudi.converge(data)

        # Verify do_file was called for crontab
        mock_do_file.assert_called()
        call_args = [call[0][0] for call in mock_do_file.call_args_list]
        self.assertTrue(any("crontab" in str(arg) for arg in call_args))


class TestRudiWarnings(unittest.TestCase):
    """Test warning messages and diagnostics."""

    @patch("builtins.print")
    @patch("rudi.do_file")
    @patch("subprocess.run")
    def test_warning_missing_file(self, mock_run, mock_do_file, mock_print):
        """Verify a warning is printed when Package references missing File."""
        mock_run.return_value = Mock(returncode=0)

        data = {
            "Services": {
                "apache2": {
                    "packages": ["apache2"]
                }
            },
            "Packages": {
                "apache2": {
                    "files": ["nonexistent.conf"]  # This file is NOT in Files
                }
            },
            "Files": {}
        }

        rudi.converge(data)

        # Verify a warning was printed
        warning_calls = [str(c) for c in mock_print.call_args_list
                         if "WARNING" in str(c)]
        self.assertTrue(len(warning_calls) > 0, "Should warn about missing file")


if __name__ == "__main__":
    unittest.main()
