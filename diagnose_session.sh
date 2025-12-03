#!/bin/bash
# Session Diagnostic Script

echo "=========================================="
echo "Flotilla Session Diagnostic"
echo "=========================================="
echo ""

# Check if config file exists
CONFIG_FILE="config/flotilla_quicksetup_config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    echo "✓ Config file found: $CONFIG_FILE"
else
    echo "✗ Config file NOT found: $CONFIG_FILE"
    echo "  Available configs:"
    ls -1 config/*.yaml 2>/dev/null || echo "  No config files found!"
fi
echo ""

# Check server connectivity
echo "Checking Server Connectivity..."
SERVER_IP="${1:-localhost}"
SERVER_PORT="12345"

echo "Testing connection to $SERVER_IP:$SERVER_PORT..."
if command -v nc &> /dev/null; then
    if nc -zv $SERVER_IP $SERVER_PORT 2>&1 | grep -q succeeded; then
        echo "✓ Server is reachable at $SERVER_IP:$SERVER_PORT"
    else
        echo "✗ Cannot reach server at $SERVER_IP:$SERVER_PORT"
        echo "  Is flo_server.py running?"
    fi
else
    echo "⚠ 'nc' command not found, skipping connectivity test"
fi
echo ""

# Try to query server for active clients
echo "Checking for active clients..."
if command -v curl &> /dev/null; then
    # Note: This is a test - the actual endpoint might be different
    echo "Attempting to connect to http://$SERVER_IP:$SERVER_PORT/"
    curl -s --connect-timeout 3 http://$SERVER_IP:$SERVER_PORT/ > /dev/null 2>&1
    if [ $? -eq 0 ] || [ $? -eq 52 ]; then
        echo "✓ Server is responding"
    else
        echo "✗ Server is not responding"
    fi
else
    echo "⚠ 'curl' command not found, skipping server test"
fi
echo ""

echo "=========================================="
echo "How to Run Session:"
echo "=========================================="
echo ""
echo "1. Make sure server is running:"
echo "   python src/flo_server.py"
echo ""
echo "2. Make sure at least one client is connected:"
echo "   python src/flo_client.py --server-ip $SERVER_IP --client-num 1"
echo ""
echo "3. Wait 10-15 seconds for client registration"
echo ""
echo "4. Run session with config file:"
echo "   python src/flo_session.py config/flotilla_quicksetup_config.yaml"
echo ""
echo "   Or if server is on different machine:"
echo "   python src/flo_session.py config/flotilla_quicksetup_config.yaml --server-ip $SERVER_IP"
echo ""
echo "=========================================="
