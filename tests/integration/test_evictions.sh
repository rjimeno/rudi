#!/bin/bash
# Test: Package eviction (removal)
# Verifies that rudi.py can remove packages using the Evictions key

set -e

echo "Running integration test: Package eviction..."

docker run --rm ubuntu:24.04 bash -c '
  apt-get update > /dev/null 2>&1
  apt-get install -y git python3-yaml cron > /dev/null 2>&1
  
  git clone https://github.com/rjimeno/rudi.git /app > /dev/null 2>&1
  cd /app
  
  # Verify cron is installed before eviction
  dpkg -l | grep -q "^ii.*cron" || exit 1
  
  # Run eviction manifest
  python3 rudi.py evictCronPhp5Apache2.yaml || true
  
  # Verify cron was removed
  ! dpkg -l | grep "^ii.*cron" > /dev/null 2>&1 || exit 1
  
  echo "✓ Package eviction successful"
'

echo "✓ Integration test PASSED: Package eviction"
