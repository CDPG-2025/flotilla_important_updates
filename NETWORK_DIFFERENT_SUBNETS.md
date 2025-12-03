# Network Configuration Issues - Different Subnets

## Problem

**Server IP:** `10.0.2.15` (VirtualBox NAT network)  
**Client IP:** `192.168.0.239` (Physical network)

**Result:** ❌ Cannot communicate - different networks!

---

## Why This Happens

`10.0.2.15` is the **default VirtualBox NAT IP**. This means:
- Your server is running in a Virtual Machine
- The VM is in NAT mode (isolated network)
- External machines cannot reach it directly

---

## ✅ Solution 1: Bridged Network Mode (RECOMMENDED)

### What is Bridged Mode?
Makes your VM appear as a real device on your network with an IP like `192.168.0.XXX`

### Steps:

#### 1. Shutdown VM
```bash
# On VM (server machine)
sudo shutdown -h now
```

#### 2. Change Network Settings

**VirtualBox:**
1. Select your VM → Settings → Network
2. Adapter 1: Change "Attached to:" from **NAT** to **Bridged Adapter**
3. Name: Select your physical network adapter (e.g., `eth0`, `wlan0`, `enp0s3`)
4. Click OK

**VMware:**
1. VM → Settings → Network Adapter
2. Select **Bridged: Connected directly to the physical network**
3. Click OK

#### 3. Start VM and Check New IP
```bash
# After VM boots up
hostname -I | awk '{print $1}'
```

**Expected output:** `192.168.0.XXX` (same subnet as client!)

#### 4. Test Connectivity
```bash
# From client machine (192.168.0.239)
ping 192.168.0.XXX  # Replace with new VM IP

# Test MQTT port
nc -zv 192.168.0.XXX 1884
```

#### 5. Run Flotilla
```bash
# On server (VM)
cd ~/Desktop/flotilla
docker-compose -f docker/docker-compose.yml up -d
python src/flo_server.py

# On client
python src/flo_client.py --server-ip 192.168.0.XXX --client-num 1
```

---

## ✅ Solution 2: Port Forwarding (Keep NAT)

If you cannot use bridged mode, forward ports from host to VM.

### Prerequisites
- Find your **host machine IP** (the physical computer running the VM)
- Host must be on same network as client (`192.168.0.XXX`)

### Steps:

#### 1. Find Host IP
```bash
# On the physical machine running VirtualBox (NOT the VM)
hostname -I | awk '{print $1}'
```
Example: `192.168.0.100`

#### 2. Configure Port Forwarding in VirtualBox

**GUI Method:**
1. VM Settings → Network → Adapter 1 → Advanced → Port Forwarding
2. Click "+" to add rules:

| Name | Protocol | Host IP | Host Port | Guest IP | Guest Port |
|------|----------|---------|-----------|----------|------------|
| MQTT | TCP | 0.0.0.0 | 1884 | 10.0.2.15 | 1884 |
| REST | TCP | 0.0.0.0 | 12345 | 10.0.2.15 | 12345 |
| gRPC1 | TCP | 0.0.0.0 | 50053 | 10.0.2.15 | 50053 |
| gRPC2 | TCP | 0.0.0.0 | 50054 | 10.0.2.15 | 50054 |

**Command Line Method:**
```bash
# Stop VM first
VBoxManage modifyvm "YourVMName" --natpf1 "MQTT,tcp,,1884,,1884"
VBoxManage modifyvm "YourVMName" --natpf1 "REST,tcp,,12345,,12345"
VBoxManage modifyvm "YourVMName" --natpf1 "gRPC1,tcp,,50053,,50053"
VBoxManage modifyvm "YourVMName" --natpf1 "gRPC2,tcp,,50054,,50054"
```

#### 3. Run Client Pointing to Host IP
```bash
# On client machine - use HOST machine IP (NOT VM IP!)
python src/flo_client.py --server-ip 192.168.0.100 --client-num 1
```

**Note:** Replace `192.168.0.100` with your actual host machine IP.

---

## ✅ Solution 3: Host-Only + NAT (Advanced)

Add a second network adapter for VM-to-Host communication.

### Steps:

#### 1. Add Second Network Adapter
**VirtualBox:**
1. VM Settings → Network → Adapter 2
2. Enable Network Adapter
3. Attached to: **Host-only Adapter**
4. Name: `vboxnet0` (or create new)

#### 2. Configure Host-Only Network
**VirtualBox → File → Host Network Manager:**
- Create/Select `vboxnet0`
- IPv4 Address: `192.168.56.1`
- IPv4 Network Mask: `255.255.255.0`
- DHCP Server: Enabled

#### 3. Check VM's New IP
```bash
# On VM
ip addr show
```
Look for interface with IP like `192.168.56.XXX`

#### 4. Problem with This Approach
❌ Client at `192.168.0.239` still cannot reach `192.168.56.XXX`  
❌ Would need routing configuration on host machine  
❌ More complex than bridged mode

**Recommendation:** Use Solution 1 (Bridged) instead!

---

## ✅ Solution 4: Run Server on Physical Machine

Skip the VM entirely for the server.

### Steps:

#### 1. Install on Host Machine
```bash
# On your physical machine (that has reachable IP)
cd ~
git clone https://github.com/CDPG-2025/flotilla_ref.git
cd flotilla_ref
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. Run Server
```bash
docker-compose -f docker/docker-compose.yml up -d
python src/flo_server.py
```

#### 3. Run Client
```bash
# On client machine
python src/flo_client.py --server-ip <HOST_IP> --client-num 1
```

---

## 🎯 Comparison Table

| Solution | Difficulty | Pros | Cons |
|----------|-----------|------|------|
| **Bridged Mode** | ⭐ Easy | Simple, VM like real machine | Requires VM restart |
| **Port Forwarding** | ⭐⭐ Medium | Keep NAT mode | Complex, limited ports |
| **Host-Only + NAT** | ⭐⭐⭐ Hard | VM isolation | Needs routing, complex |
| **Run on Host** | ⭐ Easy | No VM issues | Need to install on host |

---

## 📋 Recommended Approach

### **Use Bridged Mode (Solution 1)**

**Why?**
- ✅ Easiest to configure
- ✅ VM gets real IP on your network
- ✅ No port forwarding needed
- ✅ Works exactly like physical machine
- ✅ All ports automatically accessible

**Steps:**
1. Shutdown VM
2. VirtualBox: Settings → Network → Bridged Adapter
3. Start VM
4. Check new IP: `hostname -I`
5. Use new IP in client command

---

## 🧪 Testing Connectivity

### After Changing to Bridged Mode:

```bash
# On server (VM) - check new IP
hostname -I | awk '{print $1}'
# Should show: 192.168.0.XXX (same subnet as client)

# On client machine
ping 192.168.0.XXX
nc -zv 192.168.0.XXX 1884
nc -zv 192.168.0.XXX 12345

# All should succeed!
```

---

## 🔧 Troubleshooting

### VM Still Shows 10.0.2.15 After Bridged Mode

**Cause:** Network didn't refresh

**Fix:**
```bash
# On VM
sudo dhclient -r  # Release old IP
sudo dhclient     # Get new IP
ip addr show      # Verify new IP
```

### Cannot Select Bridged Adapter

**Cause:** No physical network adapter available

**Fix:**
- Ensure host machine is connected to network (WiFi/Ethernet)
- Try different adapter in dropdown
- Restart VirtualBox

### Bridged Mode But Still Different Subnet

**Cause:** Selected wrong adapter or DHCP issue

**Fix:**
- Select the adapter your host uses (check with `ip addr` on host)
- Manually set static IP in VM:
  ```bash
  # On VM - edit netplan or network config
  # Set IP to 192.168.0.XXX (same subnet as client)
  ```

---

## 📝 Summary

**Your Issue:**
- Server: `10.0.2.15` (VirtualBox NAT - isolated)
- Client: `192.168.0.239` (Physical network)
- Result: Cannot communicate ❌

**Best Solution:**
1. Change VM to **Bridged Network Mode**
2. VM will get IP like `192.168.0.XXX`
3. Client can now reach server ✅

**Alternative:**
- Port forwarding (more complex)
- Run server on host machine (skip VM)

---

**Next Steps:**
1. Shutdown your VM
2. Change to Bridged Mode in VirtualBox
3. Start VM and check new IP
4. Test ping from client
5. Run Flotilla with new IP

Good luck! 🚀
