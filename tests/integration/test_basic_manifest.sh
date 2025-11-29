#!/bin/bash
# Test: Basic manifest execution with file deployment
# Verifies that rudi.py can load a valid manifest and deploy files in a real Ubuntu environment

set -e

echo "Running integration test: Basic manifest execution..."

docker run --rm ubuntu:24.04 bash -c '
  apt-get update > /dev/null 2>&1
  apt-get install -y git python3-yaml > /dev/null 2>&1
  
  git clone https://github.com/rjimeno/rudi.git /app > /dev/null 2>&1
  cd /app
  
  # Run with helloPhpInfo.yaml (file deployment test)
  python3 rudi.py helloPhpInfo.yaml
  
  # Verify file was deployed
  [ -f /var/www/html/hello.php ] || exit 1
  grep -q "Hello, world" /var/www/html/hello.php || exit 1
  
  echo "✓ File deployment successful"
'

echo "✓ Integration test PASSED: Basic manifest execution"
