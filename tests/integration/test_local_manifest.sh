#!/bin/bash
# Test: Very simple manifest restarts apache2
# Verifies that rudi.py can load a valid manifest and restart service in a real Ubuntu environment

set -e

echo "Running integration test: Very simple manifest restart apache2."

docker run --rm ubuntu:24.04 bash -c '
  apt-get update > /dev/null 2>&1
  apt-get install -y git python3-yaml > /dev/null 2>&1
  
  git clone https://github.com/rjimeno/rudi.git /app > /dev/null 2>&1
  cd /app
  
  # Run with local.yaml (very simple manifest restart apache2)
  python3 rudi.py local.yaml
  
  # Verify file was deployed
  service apache2 status || exit 1
  #grep -qi "running" /var/www/html/hello.php || exit 1
  
  echo "✓ Apache2 service is running successful"
'

echo "✓ Integration test PASSED: Very simple manifest restart apache2"
