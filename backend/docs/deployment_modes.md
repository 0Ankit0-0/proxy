# Deployment Modes for Project Quorum

## 1. ISOLATED Mode (True Air-Gap)
**Use Case**: Maximum security, no network connectivity

**Configuration**:
```bash
export DEPLOYMENT_MODE=isolated
export API_HOST=127.0.0.1
```

**Features**:
- Binds to localhost only (127.0.0.1)
- No remote collection (SSH/WinRM/FTP disabled)
- USB-only log import
- Frontend must run on same machine
- Zero external dependencies at runtime

**Validation**:
```bash
curl http://localhost:8000/health/isolation
# Should return: "isolation_level": "fully_isolated"
```

---

## 2. LAN Mode (Isolated Network)
**Use Case**: Private network, multiple machines, no internet

**Configuration**:
```bash
export DEPLOYMENT_MODE=lan
export API_HOST=0.0.0.0
export ALLOWED_HOSTS=192.168.1.0/24,10.0.0.0/8
```

**Features**:
- Binds to all network interfaces
- Restricted CORS to LAN subnets
- SSH/WinRM collection within LAN
- Central analysis server model
- Agents can send logs from LAN hosts

**Network Setup**:
```
┌─────────────────────────────────────────┐
│   Isolated LAN (No Internet)            │
│                                          │
│  ┌──────────┐    ┌──────────┐          │
│  │ Server 1 │───▶│ Quorum   │          │
│  │ (Logs)   │    │ Central  │          │
│  └──────────┘    │ Analyzer │          │
│                  └──────────┘          │
│  ┌──────────┐         ▲                │
│  │ Server 2 │─────────┘                │
│  │ (Logs)   │                          │
│  └──────────┘                          │
└─────────────────────────────────────────┘
```

**Validation**:
```bash
curl http://<lan-ip>:8000/health/isolation
# Should return: "isolation_level": "lan_isolated"
```

---

## 3. USB Transfer Mode (Hybrid)
**Use Case**: Offline analysis of USB-collected logs

**Workflow**:
1. Use lightweight agent to collect logs on isolated systems
2. Export to encrypted USB drive (.qlog format)
3. Transport USB to analyst workstation
4. Import via USB endpoint for analysis

**Agent Usage** (on isolated system):
```bash
python quorum_agent.py collect --output /media/usb/logs.qlog --encrypt
```

**Analysis** (on analyst workstation):
```bash
# Start Quorum backend
python -m uvicorn app:app --host 127.0.0.1

# Import USB logs
curl -X POST http://localhost:8000/logs/collect/usb?auto_detect=true
```

---

## Comparison Table

| Feature | ISOLATED | LAN | USB Transfer |
|---------|----------|-----|--------------|
| Network Binding | 127.0.0.1 | 0.0.0.0 | 127.0.0.1 |
| Remote Collection | ❌ | ✅ (LAN only) | ❌ |
| USB Import | ✅ | ✅ | ✅ (Primary) |
| Multi-Host | ❌ | ✅ | ⚠️ (Manual) |
| Internet Required | ❌ | ❌ | ❌ |
| Real-time Monitoring | ❌ | ✅ | ❌ |
| Setup Complexity | Low | Medium | Low |

---

## Recommended Deployment

**For NTRO/Defense**: Use **ISOLATED** or **USB Transfer** mode
**For Corporate Isolated Networks**: Use **LAN** mode
**For Development/Testing**: Use **DEBUG** mode (insecure)
