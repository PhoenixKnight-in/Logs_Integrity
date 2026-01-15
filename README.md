# 🔐 SSH Brute Force Attack Event Generation & Logging

This project demonstrates **SSH brute-force attack simulation** using **Hydra** from a Kali Linux attacker machine and **event logging + synthetic event generation** on an Ubuntu Server.

It is designed for **cybersecurity attack detection, log analysis, and ML-based anomaly detection experiments**.

---

## 🧪 Lab Setup

### 🖥️ Attacker Machine
- OS: **Kali Linux**
- Tool: **Hydra**
- Purpose: Perform SSH brute-force attack

### 🖥️ Target Machine
- OS: **Ubuntu Server**
- Service: **OpenSSH**
- Purpose: Capture authentication logs and generate security events

---

## 📌 Network Configuration (Ubuntu Server)

Check the IP address of the Ubuntu Server:

```
ip a
```
#### OUTPUT:
<img width="975" height="174" alt="image" src="https://github.com/user-attachments/assets/d9f61aad-e89a-4c1a-a163-7000cb0cc912" />

---

### Continuously monitor SSH authentication logs:
```
sudo tail -f /var/log/auth.log
```
#### OUTPUT:
<img width="975" height="548" alt="image" src="https://github.com/user-attachments/assets/7ad29713-acc2-4873-b911-874dc98f3bd0" />

---

### SSH Brute Force Attack (Kali Linux)

Run Hydra to perform an SSH brute-force attack:
```
Hydra -l username -P brute_force_password.txt ssh://target_ip -t 4
```
#### OUTPUT:
<img width="1114" height="160" alt="image" src="https://github.com/user-attachments/assets/07f09e01-d64a-410a-8038-8a3f96db3077" />

---

### Event Generation (Ubuntu Server)
▶️ Normal Traffic Events
```
python3 generate_events.py --mode normal
```
▶️ Attack Simulation Events
```
python3 generate_events.py --mode attack
```
▶️ SSH Attack-Specific Events
```
python3 generate_events.py --mode ssh
```

### 📷 Sample Output:
<img width="975" height="548" alt="image" src="https://github.com/user-attachments/assets/50604611-f200-4bdf-bc2b-54e8f282060a" />

---

### 📁 Generated Events File
```
nano events.jsonl
```
<img width="975" height="548" alt="image" src="https://github.com/user-attachments/assets/a2b25104-7021-44c1-9c98-beb5f27a1a9e" />

---
