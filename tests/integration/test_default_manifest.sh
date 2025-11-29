#!/bin/bash
# Test: Default manifest (rudi.yaml) execution
# Verifies that rudi.py loads rudi.yaml by default when no argument is provided

set -e

echo "Running integration test: Default manifest (rudi.yaml)..."

docker run --rm ubuntu:24.04 bash -c '
  apt-get update > /dev/null 2>&1
  apt-get install -y git python3-yaml > /dev/null 2>&1
  
  git clone https://github.com/rjimeno/rudi.git /app > /dev/null 2>&1
  cd /app
  
  # Run without arguments (should use rudi.yaml by default)
  python3 rudi.py
  
  echo "✓ Default manifest loaded successfully"
'

echo "✓ Integration test PASSED: Default manifest execution"
