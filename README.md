# sdn-path-tracer
SDN Path Tracing Tool using Mininet and Ryu 
# SDN Path Tracing Tool using Ryu & Mininet

## 📌 Overview

This project implements a Software Defined Networking (SDN) Path Tracing Tool using the Ryu controller and Mininet.
It identifies and displays the path taken by packets across switches by analyzing real-time OpenFlow events.

---

## 🎯 Objectives

* Track flow rules installed in switches
* Identify forwarding path dynamically
* Display packet route across network
* Validate path using network tests (ping)

---

## 🧠 Core Concept

The project uses a **Ryu controller** that behaves as a learning switch.
When packets arrive:

1. The controller learns MAC-to-port mappings
2. Determines forwarding decisions
3. Installs flow rules in switches
4. Logs each hop (switch, in_port, out_port)

This allows reconstruction of the packet path.

---

## 🛠️ Technologies Used

* Python
* Ryu SDN Controller
* Mininet Network Emulator
* OpenFlow Protocol (v1.3)

---

## 📁 Project Structure

```
sdn-project/
│── path_tracer_controller.py   # Main Ryu controller (path tracing logic)
│── topology.py                # Network topology definition
│── run_topology.py            # Script to start Mininet network
│── README.md                  # Project documentation
```

---

## 🚀 How to Run

### 1️⃣ Start Ryu Controller

```
ryu-manager path_tracer_controller.py --observe-links
```

---

### 2️⃣ Run Network Topology

```
sudo python3 run_topology.py
```

---

### 3️⃣ Generate Traffic

Inside Mininet CLI:

```
h1 ping h3
```

---

## 📊 Sample Output

Controller logs:

```
[PATH] dpid=s1 in_port=1 src=00:00:00:00:00:01 dst=00:00:00:00:00:03 out_port=2
[PATH] dpid=s2 in_port=2 src=... dst=... out_port=3
[PATH] dpid=s3 in_port=1 src=... dst=... out_port=2
```

---

## 🔍 Explanation

* Each `[PATH]` log represents one hop
* `dpid` → switch ID
* `in_port` → incoming interface
* `out_port` → outgoing interface

By combining logs, the full path is obtained.

---

## ✅ Features

* Dynamic path detection (no hardcoding)
* Real-time flow rule tracking
* Protocol-aware logging (ARP, ICMP, IPv4)
* Automatic flow installation

---

## ⚠️ Limitations

* Path displayed as logs (not graphical)
* Requires Mininet environment
* Works on OpenFlow-based SDN only

---

## 🔮 Future Enhancements

* Graphical visualization of paths
* REST API for querying paths
* Multi-path and load balancing analysis
* Web-based dashboard

---

## 🎓 Conclusion

This project demonstrates how SDN controllers can monitor and analyze network behavior by observing flow rules and packet forwarding decisions, enabling dynamic path tracing in real-time.

---

## 👨‍💻 Author

Amith prasad

---
