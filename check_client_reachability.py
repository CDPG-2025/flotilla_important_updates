import socket
import sys
import time

def check_reachability(host, port):
    print(f"==================================================")
    print(f"Checking connectivity to Client at {host}:{port}...")
    print(f"==================================================")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((host, int(port)))
        
        if result == 0:
            print(f"✅ SUCCESS: Server CAN reach Client at {host}:{port}")
            print("   The network connection is good.")
            s.close()
            return True
        else:
            print(f"❌ FAILURE: Server CANNOT reach Client at {host}:{port}")
            print(f"   Error Code: {result}")
            print("\n   POSSIBLE CAUSES:")
            print("   1. FIREWALL on Client Machine is blocking port 50053")
            print("      -> Run 'sudo ufw allow 50053/tcp' on Client (Linux)")
            print("      -> Allow python/port 50053 in Windows Defender Firewall")
            print("   2. Client is NOT running")
            print("      -> Make sure 'python src/flo_client.py ...' is running")
            print("   3. Network Routing Issue")
            print("      -> Can you ping the client IP from here?")
            s.close()
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_client_reachability.py <CLIENT_IP> [PORT]")
        print("Default PORT is 50053 (Client 1)")
        print("Example: python check_client_reachability.py 192.168.0.239")
        sys.exit(1)
    
    client_ip = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else "50053"
    
    check_reachability(client_ip, port)
