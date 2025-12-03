# Session Terminating Immediately - Troubleshooting Guide

## Problem

The session (`flo_session.py`) terminates immediately without waiting or starting training.

---

## Common Causes & Solutions

### ❌ **Cause 1: Missing Config File Argument**

**Symptom:**
```bash
python src/flo_session.py
# Error: the following arguments are required: config_path
```

**Solution:**
```bash
# You MUST provide a config file path
python src/flo_session.py config/flotilla_quicksetup_config.yaml
```

---

### ❌ **Cause 2: No Active Clients**

**Symptom:**
```bash
[FLOW] flo_session.py: Request failed with status code 400
Response JSON: {'message': 'No active clients'}
```

**Why:** The server has no connected clients yet.

**Solution:**

1. **Start at least one client FIRST:**
   ```bash
   # On client machine
   python src/flo_client.py --server-ip <SERVER_IP> --client-num 1
   ```

2. **Wait 10-15 seconds** for client to register with server

3. **Then run session:**
   ```bash
   python src/flo_session.py config/flotilla_quicksetup_config.yaml
   ```

---

### ❌ **Cause 3: Session Already Running**

**Symptom:**
```bash
[FLOW] flo_session.py: Request failed with status code 400
Response JSON: {'message': 'A session is already running'}
```

**Solution:**

Wait for the current session to finish, or restart the server:
```bash
# Stop server (Ctrl+C)
# Restart server
python src/flo_server.py
```

---

### ❌ **Cause 4: Cannot Connect to Server**

**Symptom:**
```bash
[ERROR] Could not connect to Flotilla Server at http://localhost:12345/execute_command
```

**Why:** Server is not running or wrong IP/port.

**Solution:**

1. **Check if server is running:**
   ```bash
   # Should see flo_server.py process
   ps aux | grep flo_server
   ```

2. **If not running, start it:**
   ```bash
   python src/flo_server.py
   ```

3. **If server is on different machine, specify IP:**
   ```bash
   python src/flo_session.py config/flotilla_quicksetup_config.yaml --server-ip 192.168.0.XXX
   ```

---

### ❌ **Cause 5: Wrong Server IP**

**Symptom:**
```bash
[ERROR] Could not connect to Flotilla Server at http://10.0.2.15:12345/execute_command
```

**Solution:**

Use the correct server IP (not Docker IP, not NAT IP):
```bash
# Find server IP on server machine
hostname -I | awk '{print $1}'

# Use that IP in session command
python src/flo_session.py config/flotilla_quicksetup_config.yaml --server-ip <CORRECT_IP>
```

---

### ❌ **Cause 6: Config File Not Found**

**Symptom:**
```bash
FileNotFoundError: [Errno 2] No such file or directory: 'config/flotilla_quicksetup_config.yaml'
```

**Solution:**

1. **Check available config files:**
   ```bash
   ls -l config/*.yaml
   ```

2. **Use the correct path:**
   ```bash
   # If you have a different config file
   python src/flo_session.py config/my_training_config.yaml
   ```

---

## ✅ Correct Startup Sequence

### **Step-by-Step Process:**

#### **1. Start Server (Server Machine)**
```bash
cd ~/Desktop/flotilla
source .venv/bin/activate

# Terminal 1: Docker
docker-compose -f docker/docker-compose.yml up -d

# Terminal 2: Server
python src/flo_server.py
```

**Wait for:**
```
============================================================
SERVER IP ADDRESS: 192.168.0.100
============================================================
Server listening on 0.0.0.0:12345
```

---

#### **2. Start Client(s) (Client Machine or Same Machine)**
```bash
cd ~/Desktop/flotilla  # or ~/Documents/flotilla_ref on client
source .venv/bin/activate  # or venv311/bin/activate

python src/flo_client.py --server-ip 192.168.0.100 --client-num 1
```

**Wait for:**
```
============================================================
CLIENT IP ADDRESS: 192.168.0.239
============================================================
Overriding MQTT Broker IP to: 192.168.0.100
✓ MQTT connected
✓ gRPC server started
```

---

#### **3. Wait 10-15 Seconds**

Give the client time to:
- Connect to MQTT broker
- Register with server
- Send heartbeat messages

---

#### **4. Start Session (Server Machine or Any Machine)**
```bash
cd ~/Desktop/flotilla
source .venv/bin/activate

python src/flo_session.py config/flotilla_quicksetup_config.yaml
```

**If server is on different machine:**
```bash
python src/flo_session.py config/flotilla_quicksetup_config.yaml --server-ip 192.168.0.100
```

**Expected Output:**
```
[FLOW] flo_session.py: Sending POST request to http://192.168.0.100:12345/execute_command
[FLOW] flo_session.py: Request was successful!
Response JSON: {'message': 'Session <session-id> finished'}
```

---

## 🧪 Diagnostic Commands

### **Check Server Status**
```bash
# Is server running?
ps aux | grep flo_server.py

# Is server listening on port 12345?
netstat -tulpn | grep 12345

# Test server connectivity
curl http://localhost:12345
# Or from remote machine:
curl http://192.168.0.100:12345
```

### **Check Client Status**
```bash
# Is client running?
ps aux | grep flo_client.py

# Check client logs for "MQTT connected"
# Should see in client output
```

### **Check Docker Services**
```bash
# Are MQTT and Redis running?
docker ps

# Should show:
# - mqtt_broker (port 1884)
# - redis_server (port 6379)
```

---

## 📋 Session Command Reference

### **Basic Usage (Server on Same Machine)**
```bash
python src/flo_session.py config/flotilla_quicksetup_config.yaml
```

### **Server on Different Machine**
```bash
python src/flo_session.py config/flotilla_quicksetup_config.yaml --server-ip 192.168.0.100
```

### **Custom Port**
```bash
python src/flo_session.py config/flotilla_quicksetup_config.yaml --server-ip 192.168.0.100 --server-port 12345
```

### **Restore Previous Session**
```bash
python src/flo_session.py config/flotilla_quicksetup_config.yaml --restore --session_id <SESSION_ID>
```

---

## 🔍 Debug Mode

### **Run with Verbose Output**

Add print statements to see what's happening:

```bash
# Check what config is being sent
python src/flo_session.py config/flotilla_quicksetup_config.yaml
```

The script will print:
1. The full configuration being sent
2. The API URL it's connecting to
3. The response from server

---

## ✅ Quick Checklist

Before running session, verify:

- [ ] **Server is running** (`python src/flo_server.py`)
- [ ] **Docker is running** (`docker ps` shows mqtt_broker and redis_server)
- [ ] **At least one client connected** (see "MQTT connected" in client output)
- [ ] **Waited 10-15 seconds** after client connection
- [ ] **Config file exists** (`ls config/flotilla_quicksetup_config.yaml`)
- [ ] **Correct server IP** (not 172.17.x.x, not 10.0.2.15 if NAT)
- [ ] **Port 12345 accessible** (firewall allows it)

---

## 🎯 Most Common Issue

**Problem:** "No active clients"

**Cause:** Session started before client registered

**Solution:**
1. Start client
2. **Wait 10-15 seconds** (important!)
3. Then start session

---

## 📝 Example: Complete Flow

### **Server Machine (192.168.0.100)**
```bash
# Terminal 1
docker-compose -f docker/docker-compose.yml up -d

# Terminal 2
python src/flo_server.py
# Wait for: "Server listening on 0.0.0.0:12345"
```

### **Client Machine (192.168.0.239)**
```bash
python src/flo_client.py --server-ip 192.168.0.100 --client-num 1
# Wait for: "MQTT connected"
```

### **Wait 15 seconds** ⏱️

### **Server Machine (Terminal 3)**
```bash
python src/flo_session.py config/flotilla_quicksetup_config.yaml
# Should start training!
```

---

## 🛠️ Run Diagnostic Script

I've created a diagnostic script to help:

```bash
cd ~/Desktop/flotilla
./diagnose_session.sh

# Or for remote server:
./diagnose_session.sh 192.168.0.100
```

This will check:
- Config file exists
- Server is reachable
- Proper command syntax

---

## 💡 Pro Tips

1. **Always wait 10-15 seconds** after starting clients before running session
2. **Check server logs** to see if clients registered
3. **Use `--server-ip` argument** when server is on different machine
4. **Ensure config file path is correct** (it's a required argument)
5. **One session at a time** - wait for previous session to finish

---

**Need more help?** Share the exact output/error message you're seeing!
