#!/bin/bash
# Test: Cron configuration deployment
# Verifies that rudi.py can deploy cron configuration files and restart services

set -e

echo "Running integration test: Cron configuration deployment..."

docker run --rm ubuntu:24.04 bash -c '
  apt-get update > /dev/null 2>&1
  apt-get install -y git python3-yaml cron > /dev/null 2>&1
  
  git clone https://github.com/rjimeno/rudi.git /app > /dev/null 2>&1
  cd /app
  
  # Run cron manifest
  python3 rudi.py cron.yaml
  
  # Verify crontab was deployed
  [ -f /etc/crontab ] || exit 1
  grep -q "cron.hourly" /etc/crontab || exit 1
  
  # Verify cron service is running
  service cron status > /dev/null 2>&1 || exit 1
  
  echo "✓ Cron configuration deployed successfully"
'

echo "✓ Integration test PASSED: Cron configuration deployment"
