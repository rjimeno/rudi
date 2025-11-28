"""Tests for rudi module constants and configuration."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rudi


class TestRudiConstants(unittest.TestCase):
    """Test that rudi module constants are properly defined."""

    def test_system_command_constants_exist(self):
        """Verify all system command constants are defined."""
        self.assertTrue(hasattr(rudi, "CHGRP"))
        self.assertTrue(hasattr(rudi, "CHMOD"))
        self.assertTrue(hasattr(rudi, "CHOWN"))
        self.assertTrue(hasattr(rudi, "DPKG"))
        self.assertTrue(hasattr(rudi, "SERVICE"))

    def test_dpkg_uses_apt_get(self):
        """Verify DPKG constant points to apt-get."""
        self.assertIn("apt-get", rudi.DPKG)

    def test_service_command_path(self):
        """Verify SERVICE constant points to valid service command."""
        self.assertIn("service", rudi.SERVICE)

    def test_default_config_file(self):
        """Verify DEFAULT_CONF is set to rudi.yaml."""
        self.assertEqual(rudi.DEFAULT_CONF, "rudi.yaml")


class TestRudiHelpers(unittest.TestCase):
    """Test helper/utility behaviors in rudi."""

    def test_rudi_has_do_file_function(self):
        """Verify do_file function is defined."""
        self.assertTrue(hasattr(rudi, "do_file"))
        self.assertTrue(callable(rudi.do_file))

    def test_rudi_has_converge_function(self):
        """Verify converge function is defined."""
        self.assertTrue(hasattr(rudi, "converge"))
        self.assertTrue(callable(rudi.converge))


if __name__ == "__main__":
    unittest.main()
