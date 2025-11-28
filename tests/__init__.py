"""Test configuration and pytest fixtures."""

import sys
import os

# Ensure rudi module can be imported from tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
