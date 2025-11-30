#!/bin/bash
# Troubleshoot: Starts a container for manual testing and troubleshooting.

set -e

echo ""
docker run --rm -it ubuntu:24.04 bash -c '
  echo "This troubleshooting container will need a few things installed before it is ready..."
  echo ""
  apt update
  # DEBIAN_FRONTEND=noninteractive apt-get install -y git python3-yaml
  echo ""
  apt install git 
  echo ""
  git clone https://github.com/rjimeno/rudi.git /app && cd /app
  echo ""
  apt install python3-yaml
  echo ""
  echo "✓ The interactive troubleshooting session is ready."
  echo "Type 'exit' or press Ctrl+D on an empty line to leave the container."
  echo ""
  echo "You can run rudi.py with your manifests."
  echo "For example, to run the helloPhpInfo.yaml manifest, use:"
  echo "  python3 rudi.py helloPhpInfo.yaml"
  echo ""
  exec bash
  echo "The interactive troubleshootingsession is ending."
'
echo "✓ The troubleshooting container has been reapped."
