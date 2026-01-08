# Ambient Wi-Fi Monitor - System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AMBIENT WI-FI MONITOR                            │
│              Professional Environmental Intelligence                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          CLI Interface (main.py)                     │
│  Commands: scan | monitor | status | baseline | report              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     COMPLIANCE VALIDATOR                             │
│         Enforces ethical and legal constraints                       │
│  ❌ No packet sniffing  ❌ No tracking  ❌ No attacks               │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                  ▼
┌──────────────────────┐          ┌──────────────────────┐
│   DATA COLLECTION    │          │   DATA STORAGE       │
│                      │          │                      │
│ • WlanInterface      │◄────────►│ • Raw Data Store     │
│ • WlanNetworks       │          │ • Normalized Store   │
│ • IpConfig           │          │ • Baseline Store     │
│ • Arp                │          │ • Metadata Store     │
└──────────┬───────────┘          └──────────┬───────────┘
           │                                  │
           ▼                                  ▼
┌──────────────────────┐          ┌──────────────────────┐
│  DATA NORMALIZATION  │          │   HISTORICAL DATA    │
│                      │          │                      │
│ • Parse raw outputs  │          │ • JSON files         │
│ • Structure data     │          │ • CSV exports        │
│ • Extract features   │          │ • Time-series data   │
└──────────┬───────────┘          └──────────┬───────────┘
           │                                  │
           └────────────────┬─────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       ANALYSIS ENGINES                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ BASELINE MODEL   │  │ TEMPORAL ANALYSIS│  │ ANOMALY DETECTOR │ │
│  │                  │  │                  │  │                  │ │
│  │ • Learn normal   │  │ • Short-term     │  │ • Z-score        │ │
│  │ • Statistics     │  │ • Medium-term    │  │ • IQR method     │ │
│  │ • Confidence     │  │ • Long-term      │  │ • Sudden changes │ │
│  │ • Auto-update    │  │ • Trend detect   │  │ • Confidence     │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              ENVIRONMENTAL FINGERPRINTING                      │ │
│  │                                                                │ │
│  │  • Feature extraction    • Similarity scoring                 │ │
│  │  • Hash generation       • Pattern matching                   │ │
│  │  • Aggregation           • Environment comparison             │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      REPORTING SYSTEM                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────┐      ┌─────────────────────────┐      │
│  │   TEXT REPORTS          │      │   JSON REPORTS          │      │
│  │                         │      │                         │      │
│  │ • Human-readable        │      │ • Machine-readable      │      │
│  │ • Detective-style       │      │ • API-friendly          │      │
│  │ • Confidence-aware      │      │ • Structured data       │      │
│  │ • Interpretations       │      │ • Programmatic access   │      │
│  └─────────────────────────┘      └─────────────────────────┘      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Windows OS Commands
       │
       ├─► netsh wlan show interfaces
       ├─► netsh wlan show networks mode=bssid
       ├─► ipconfig /all
       └─► arp -a
              │
              ▼
       Raw Text Output
              │
              ▼
       Normalization
              │
              ├─► Extract BSSIDs, SSIDs
              ├─► Parse signal strengths
              ├─► Identify channels
              └─► Structure metadata
                     │
                     ▼
              JSON Storage
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
   Baseline Model            Time-Series Data
       │                           │
       └────────┬──────────────────┘
                ▼
         Analysis Results
                │
                ├─► Environmental Status
                ├─► Temporal Trends
                ├─► Anomaly Alerts
                └─► Fingerprint Match
                       │
                       ▼
                 Reports (Text/JSON)
```

## Key Principles

### 1. Read-Only Operations
- No modifications to networks
- No active probing
- No packet injection
- OS-level commands only

### 2. Privacy-Preserving
- No long-term device tracking
- Aggregate analysis only
- No person identification
- Focus on environmental patterns

### 3. Confidence-Aware
- All conclusions include confidence scores
- Explicit uncertainty communication
- Relative comparisons preferred
- Assumptions clearly stated

### 4. Deterministic Behavior
- Same inputs → same outputs
- Reproducible analysis
- Auditable processing
- Transparent methodology

## Analysis Strategy

### Baseline Establishment
```
Observation 1-99:  Provisional baseline (low confidence)
Observation 100+:  Stable baseline (high confidence)
Every 10 obs:      Baseline update (rolling improvement)
```

### Temporal Windows
```
Short-term:   10 observations  (~10 minutes at 60s interval)
Medium-term:  50 observations  (~50 minutes)
Long-term:    200 observations (~3.3 hours)
```

### Anomaly Thresholds
```
Z-score > 3.0:     High severity anomaly
Z-score > 2.0:     Medium severity
Sudden change >50%: Spike/drop detection
CV > 2.0:          Signal instability
```

### Fingerprint Features
```
• BSSID count
• SSID count  
• RSSI mean
• RSSI std deviation
• Channel diversity
• Signal stability
```

## Extensibility Points

### Future Sensor Integration
```
┌──────────────┐
│ ESP32 Sensor │──┐
└──────────────┘  │
                  ├──► Data Collection
┌──────────────┐  │      Orchestrator
│ Raspberry Pi │──┘
└──────────────┘
```

### Future Analysis Modules
- Machine learning pattern recognition
- Multi-location correlation
- Predictive modeling
- Long-term trend forecasting

### Future Visualization
- Real-time dashboards
- Historical charts
- Network graphs
- Heatmaps

## Security Considerations

### Data Protection
- Local storage only (no cloud)
- Configurable retention
- Optional data encryption
- Audit logging

### Access Control
- Administrator privileges required
- Compliance validation on every operation
- Prohibited operations raise exceptions
- Explicit permission checks

## Performance Profile

### Resource Usage
- CPU: Minimal (command execution + analysis)
- Memory: ~50-100 MB typical
- Disk: ~1-5 MB per hour (depends on environment)
- Network: None (local OS commands only)

### Scalability
- Single-location: Handles continuous monitoring indefinitely
- Multi-location: Design supports future extension
- Long-term: Automatic data retention management

---

**Design Philosophy**: Treat Wi-Fi as an environmental signal, not as individual devices.
This is environmental sensing, not network diagnostics.
