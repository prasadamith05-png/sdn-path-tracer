# 🚀 SDN Path Tracing Tool (Without Mininet)

## 📌 Overview

This project simulates **Software Defined Networking (SDN) path tracing** without using Mininet.
It uses Python and NetworkX to:

* Build a network topology
* Dynamically compute shortest paths
* Simulate flow rules
* Handle link failures

---

## 📂 Project Files

* `sdn-path-tracker.py` → Main simulation program 
* `controller.py` → Ryu controller logic (optional, Mininet-based) 
* `topo.py` → Mininet topology (not required here) 

👉 For this project, we only use:
✅ `sdn-path-tracker.py`

---

## 🛠️ Requirements

Make sure Ubuntu has:

* Python 3
* pip

Install required library:

```bash
pip3 install networkx
```

---

## ▶️ How to Run (Ubuntu)

### Step 1: Open Terminal

Press:

```
Ctrl + Alt + T
```

---

### Step 2: Go to Project Folder

```bash
cd path/to/your/project
```

---

### Step 3: Run the Program

```bash
python3 sdn-path-tracker.py
```

---

## 🧠 Features

### ✅ 1. Path Tracing

* Uses Dijkstra algorithm
* Finds shortest path between hosts

### ✅ 2. Flow Table Learning

* Switches dynamically learn forwarding rules

### ✅ 3. Link Failure Simulation

* Random link failure testing
* Recomputes path automatically

### ✅ 4. Dynamic Network Conditions

* Random latency added to links

---

## 📊 Example Output

```
====== SDN PATH TRACER (ADVANCED) ======

1. Trace Path
2. Show Flow Table
3. Simulate Link Failure
4. Exit

Enter choice: 1

Selected Path: H1 -> S1 -> S3 -> H3
Total Cost (Latency): 12

[Switch S1]
Flow Rule Applied: if dest=H3 → output:S3
```

---

## ⚠️ Notes

* ❌ No Mininet required
* ❌ No Ryu controller required
* ✅ Fully Python-based simulation


---

## 🧩 Future Improvements

* GUI visualization
* Real-time packet simulation
* Integration with Mininet
* Web dashboard

---

## 👨‍💻 Author

SDN Path Tracing Simulation Project (Ubuntu Based)
AMITH PRASAD S G
---
