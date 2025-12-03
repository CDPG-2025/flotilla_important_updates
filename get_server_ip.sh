#!/bin/bash
# Script to find the correct server IP for multi-machine deployment

echo "==================================================="
echo "Finding Server IP Address"
echo "==================================================="
echo ""

echo "Method 1: hostname -I"
hostname -I | awk '{print "Primary IP: " $1}'
echo ""

echo "Method 2: ip addr (all interfaces)"
ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1
echo ""

echo "Method 3: Using Python socket"
python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print('Recommended IP:', s.getsockname()[0]); s.close()"
echo ""

echo "==================================================="
echo "Use the IP from your network range (e.g., 192.168.x.x)"
echo "NOT the Docker IP (172.17.x.x)"
echo "==================================================="
