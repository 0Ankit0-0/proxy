# 🚀 Project Quorum — Features & Architecture

**Smart India Hackathon 2025 – Problem Statement SIH25235**  
**Theme:** Offline, Portable Forensics  
**Team:** Quorum.pkl  
**Category:** Software  
**Focus:** Secure Offline Log Intelligence Platform

---

## 🧠 Project Overview

**Project Quorum** is an *AI-powered, offline log analysis tool* designed for air-gapped and isolated networks such as NTRO, Defense, and Critical Infrastructure systems.

It combines **portability**, **embedded AI**, and **secure offline updates** to provide enterprise-grade cybersecurity analytics without cloud or server dependencies.

---

## 🧩 Core Features

| Feature | Description |
|----------|-------------|
| **Portable Offline Execution** | Runs directly from an encrypted USB or local folder. No installation or internet required. |
| **Multi-Source Log Collection** | Collects logs from Windows, Linux, and network devices via SSH, WinRM, or file import. |
| **Unified Log Parsing & Storage** | Parses multiple log formats (Syslog, EVTX, JSON) into a unified format stored in DuckDB. |
| **AI-Powered Detection** | Uses TensorFlow Lite + PyOD for on-device anomaly and outlier detection. |
| **Secure Offline Update Protocol (SOUP)** | Digitally signed update mechanism for AI models, parsing rules, and threat intel. |
| **Embedded Database** | DuckDB ensures high-speed, in-process analytics without requiring servers. |
| **Web Dashboard (Localhost)** | React + Tailwind frontend provides real-time visualization, reports, and anomaly insights. |
| **Cross-Platform Support** | Works on Windows, macOS, and Linux. Agents handle OS-specific log sources automatically. |

---

## 🏗️ System Architecture

                      ┌────────────────────────────────────┐
                      │      Project Quorum Hub (Main)     │
                      │────────────────────────────────────│
                      │ • FastAPI Backend (Python, Async)  │
                      │ • DuckDB Embedded DB               │
                      │ • TensorFlow Lite + PyOD Engine    │
                      │ • SOUP (Offline Update Protocol)   │
                      │ • React + Tailwind Web Dashboard   │
                      └────────────────────────────────────┘
                                      ▲
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
         [LAN A] Defense Net   [LAN B] CyberOps Net   [LAN C] R&D Net
                    │                 │                 │
        ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
        │ Quorum Agent  │   │ Quorum Agent  │   │ Quorum Agent  │
        │ (Linux/Win)   │   │ (Linux/Win)   │   │ (Linux/Win)   │
        │---------------│   │---------------│   │---------------│
        │ • SSH / WinRM │   │ • SSH / WinRM │   │ • SSH / WinRM │
        │ • AES Encrypt │   │ • AES Encrypt │   │ • AES Encrypt │
        │ • Hash Verify │   │ • Hash Verify │   │ • Hash Verify │
        └───────────────┘   └───────────────┘   └───────────────┘
                    │                 │                 │
         ┌──────────┴──────────┐ ┌────┴────┐  ┌────────┴────────┐
         │ Local Log Storage   │ │ Log Sync │  │ Offline Export  │
         │ (/var/log/, etc.)   │ │ via LAN  │  │ via USB (SOUP)  │
         └─────────────────────┘ └──────────┘  └─────────────────┘


---

## ⚙️ Component Breakdown

### **1. Backend – FastAPI**
- Serves as the main command & control API.
- Handles:
  - Log ingestion from agents
  - File uploads (`.qlog` or `.zip`)
  - Parsing and database storage
  - AI inference calls (TensorFlow Lite + PyOD)
- Exposes endpoints for the frontend dashboard.

**Key Modules**
- `routes/logs.py` → Log collection and parsing
- `routes/analysis.py` → AI-based anomaly detection
- `routes/soup.py` → Offline update and signature validation

---

### **2. Database – DuckDB**
- Embedded analytical database (no setup required).
- Stores structured logs, parsed events, and ML results.
- Query performance comparable to PostgreSQL.
- Operates fully in-memory or on local `.db` file.

**Advantages**
- Perfect for air-gapped systems.
- Fast SQL analytics on large log files.
- Lightweight (< 10 MB binary).

---

### **3. AI Engine – TensorFlow Lite + PyOD**
- **TensorFlow Lite** → Runs pretrained ML models for classification/anomaly detection.
- **PyOD** → Ensemble of outlier detectors (LOF, IsolationForest, AutoEncoder).
- **Hybrid Mode**: Combines both methods for better accuracy and speed.

**Example Workflow**
1. Logs parsed and converted to feature vectors.
2. Model loaded from `/models/tflite/`.
3. Inference executed on-device.
4. Anomalies flagged and stored in `analysis_results` table.

---

### **4. Frontend – React + Tailwind**
- Interactive local dashboard (`localhost:5173`).
- Displays:
  - System Overview
  - Timeline View
  - Anomaly Reports
  - SOUP Update Status
- Optional build using **Tauri** for cross-platform executables (`.exe`, `.AppImage`).

---

### **5. Log Collectors (Python Agents)**
- Standalone scripts deployable in isolated networks.
- Collect system logs:
  - **Windows:** Event Viewer, PowerShell, Security, Sysmon.
  - **Linux:** `/var/log/syslog`, `/auth.log`, journalctl.
- Compress + Encrypt logs (`AES256`), and send via:
  - **Online:** SSH / WinRM
  - **Offline:** Export `.qlog` (signed package)

---

### **6. SOUP (Secure Offline Update Protocol)**
Handles safe, one-click offline updates.

**Update Workflow**
1. Admin system downloads AI/rule updates.
2. Bundles into `.sentinelupdate` package.
3. Digitally signs with private key.
4. Analyst imports via USB.
5. Project Quorum validates signature & checksum.
6. Updates applied atomically.

---

## 🔐 Security Design

| Security Layer | Implementation |
|----------------|----------------|
| Log Encryption | AES-256 symmetric encryption (Fernet) |
| Data Integrity | SHA-512 checksums + signature verification |
| Communication | SSH (Linux) / WinRM (Windows) |
| Executable Protection | PyInstaller encryption or Tauri build |
| Offline Updates | Digitally signed `.qpkg` or `.qlog` |
| Database Security | DuckDB read-only query mode for viewing |

---

## 🧩 Supported Log Types (MVP)
- Syslog (Linux)
- Windows Event Logs (EVTX)
- Firewall Logs (Generic)
- Application Logs (JSON / TXT)
- Custom Parsers via YAML/Regex (Post-MVP)

---

## 🗓️ Development Phases (Short Summary)

| Phase | Focus |
|-------|--------|
| **Phase 1** | Core architecture, backend setup, and basic log collector |
| **Phase 2** | DuckDB integration and AI engine (PyOD + TFLite) |
| **Phase 3** | Frontend dashboard & SOUP update logic |
| **Phase 4** | Packaging, testing, and offline USB demo for SIH |

---

## 🧭 Summary

Project Quorum bridges the gap between traditional online SIEMs and real-world offline security environments.  
Its **AI-powered**, **portable**, and **secure** architecture empowers analysts in air-gapped networks to detect and respond to cyber threats—without internet or infrastructure.

---

**Author:** Team Quorum.pkl  
**Version:** 1.0.0  
**Maintained by:** [Backend Team Lead — Ankit Vishwakarma, Asmith Mahendrakar]  
**Date:** 2025-10-18
