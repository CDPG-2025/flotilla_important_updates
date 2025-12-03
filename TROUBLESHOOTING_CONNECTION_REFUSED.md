# 🚨 Troubleshooting: Connection Refused Error

## Problem

```
ConnectionRefusedError: [Errno 111] Connection refused
Connecting to MQTT broker 172.17.0.1:1884
```

## Root Cause

You're using the **Docker bridge IP** (`172.17.0.1`) instead of the **actual server machine IP**.

- `172.17.0.1` is Docker's internal network on the server machine
- Client machines **cannot** reach this IP
- You need the server's **real network IP** (e.g., `192.168.x.x`)

---

## ✅ Solution

### Step 1: Find the Correct Server IP

**On the server machine**, run one of these commands:

#### Option A: Quick Command
```bash
hostname -I | awk '{print $1}'
```

#### Option B: Use the helper script
```bash
cd ~/Desktop/flotilla
./get_server_ip.sh
```

#### Option C: Python method
```bash
python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()"
```

**Expected output:** Something like `192.168.0.100` or `192.168.1.100` (NOT `172.17.0.1`)

---

### Step 2: Run Client with Correct IP

**On the client machine**, use the IP you found above:

```bash
# Replace 192.168.0.100 with YOUR server's actual IP
python src/flo_client.py --server-ip 192.168.0.100 --client-num 1
```

**Example:**
If your server IP is `192.168.0.100`:
```bash
cd ~/Documents/flotilla_ref
source venv311/bin/activate
python src/flo_client.py --server-ip 192.168.0.100 --client-num 1
```

---

## 🔍 How to Identify the Correct IP

### ✅ Correct IPs (Use These)
- `192.168.x.x` - Private network (most common)
- `10.x.x.x` - Private network
- `172.16.x.x` to `172.31.x.x` - Private network
- Public IP if on cloud/internet

### ❌ Wrong IPs (Don't Use These)
- `127.0.0.1` - Localhost (only works on same machine)
- `172.17.x.x` - Docker bridge network (internal to Docker)
- `172.18.x.x` - Docker custom networks (internal to Docker)
- `0.0.0.0` - Bind address (not a connection address)

---

## 📋 Complete Example

### Server Machine (IP: 192.168.0.100)

```bash
# Terminal 1: Start Docker
cd ~/Desktop/flotilla
docker-compose -f docker/docker-compose.yml up -d

# Terminal 2: Start Server
cd ~/Desktop/flotilla
source .venv/bin/activate
python src/flo_server.py

# You should see:
# ============================================================
# SERVER IP ADDRESS: 192.168.0.100
# Clients should connect using: --server-ip 192.168.0.100
# ============================================================
```

### Client Machine (IP: 192.168.0.239)

```bash
cd ~/Documents/flotilla_ref
source venv311/bin/activate
python src/flo_client.py --server-ip 192.168.0.100 --client-num 1

# You should see:
# ============================================================
# CLIENT IP ADDRESS: 192.168.0.239
# ============================================================
# Overriding MQTT Broker IP to: 192.168.0.100
# ✓ MQTT connected
```

---

## 🧪 Test Network Connectivity

Before running the client, verify connectivity:

### Test 1: Ping Server
```bash
# From client machine
ping 192.168.0.100
```

### Test 2: Check MQTT Port
```bash
# From client machine
nc -zv 192.168.0.100 1884
```

**Expected:** `Connection to 192.168.0.100 1884 port [tcp/*] succeeded!`

### Test 3: Check REST API Port
```bash
# From client machine
curl http://192.168.0.100:12345
```

---

## 🔧 If Still Not Working

### Check Server Firewall

**On server machine:**
```bash
# Allow MQTT port
sudo ufw allow 1884/tcp

# Allow REST API port
sudo ufw allow 12345/tcp

# Check firewall status
sudo ufw status
```

### Check Docker is Running

**On server machine:**
```bash
docker ps

# Should show:
# - mqtt_broker (port 1884)
# - redis_server (port 6379)
```

### Check MQTT Broker is Accessible

**On server machine:**
```bash
# Check if MQTT is listening on all interfaces
netstat -tulpn | grep 1884

# Should show: 0.0.0.0:1884 (not 127.0.0.1:1884)
```

If it shows `127.0.0.1:1884`, you need to update Docker configuration:

**Edit `docker/docker-compose.yml`:**
```yaml
services:
  mqtt_broker:
    ports:
      - "0.0.0.0:1884:1883"  # Bind to all interfaces
```

Then restart Docker:
```bash
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d
```

---

## 📝 Quick Checklist

- [ ] Server IP is NOT `172.17.x.x` (Docker IP)
- [ ] Server IP is NOT `127.0.0.1` (localhost)
- [ ] Server IP is in same network range as client (e.g., both `192.168.0.x`)
- [ ] Can ping server from client machine
- [ ] Port 1884 is open on server firewall
- [ ] Docker containers are running on server
- [ ] MQTT broker is listening on `0.0.0.0:1884` (not `127.0.0.1:1884`)
- [ ] Using correct command: `python src/flo_client.py --server-ip <REAL_SERVER_IP> --client-num 1`

---

## 🎯 Summary

**Problem:** Client trying to connect to Docker IP `172.17.0.1`

**Solution:** Use the server's actual network IP (e.g., `192.168.0.100`)

**Command:**
```bash
# Find server IP on server machine
hostname -I | awk '{print $1}'

# Run client with correct IP
python src/flo_client.py --server-ip <ACTUAL_SERVER_IP> --client-num 1
```

---

**Need more help?** Check `QUICK_START_MULTI_MACHINE.md` for complete setup instructions.
