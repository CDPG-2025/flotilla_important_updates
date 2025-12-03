# 🚨 Troubleshooting: Session Terminates Immediately (No Rounds)

## Problem

You run the session, it says "Session finished", but **no training rounds happened**.

## Root Cause

**The Server cannot connect to the Client.**

In Flotilla, communication is **Bi-Directional**:
1. **Client -> Server (MQTT)**: Works (Client registers).
2. **Server -> Client (gRPC)**: **FAILS** (Firewall blocks Server).

If the Server cannot send the "Start Training" command to the Client (port 50053), it marks the client as dead and finishes the session immediately.

---

## ✅ Solution: Allow Incoming Connections on Client

You need to open port **50053** (and 50054, etc.) on the **Client Machine**.

### **If Client is Linux (Ubuntu/Debian):**
Run this on the **Client Machine**:
```bash
sudo ufw allow 50053/tcp
sudo ufw allow 50054/tcp
sudo ufw reload
```

### **If Client is Windows:**
1. Open **Windows Defender Firewall with Advanced Security**.
2. Click **Inbound Rules** -> **New Rule**.
3. Select **Port** -> **TCP**.
4. Specific local ports: `50053-50060`.
5. **Allow the connection**.
6. Name it "Flotilla gRPC".

### **If Client is macOS:**
1. System Settings -> Network -> Firewall.
2. Options -> Allow incoming connections for `python`.

---

## 🧪 Verify the Fix

### **1. Run the Verification Script (On Server)**
I've created a script to test this. Run it on the **Server Machine**:

```bash
# Replace with your Client's IP
python check_client_reachability.py 192.168.0.239
```

**If it says ❌ FAILURE:**
- The Firewall is still blocking the port.
- Or the Client is not running.

**If it says ✅ SUCCESS:**
- Run the session again, it should work!

---

## 📝 Summary

1. **Start Server** (Server Machine).
2. **Start Client** (Client Machine).
3. **Run `python check_client_reachability.py <CLIENT_IP>`** on Server.
4. If successful, **Start Session**.

---

### **Note on Multiple Clients**
- Client 1: Ports 50053, 50054
- Client 2: Ports 50055, 50056
- Client 3: Ports 50057, 50058

Make sure to allow the range `50053:50060` if running multiple clients.
