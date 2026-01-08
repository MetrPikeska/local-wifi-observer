# Ambient Wi-Fi Monitor

**Professional Wi-Fi Environmental Intelligence System**

## Overview

Ambient Wi-Fi Monitor is a serious, ethical, and forensic-grade Python application for deep, read-only analysis of the Wi-Fi environment surrounding a Windows laptop. This is **not** a hacking tool, network diagnostic utility, or device tracker. It is an environmental sensing instrument that treats Wi-Fi as an aggregate signal source for analytical intelligence.

## Philosophy

This tool is designed to:
- Extract maximum truthful, defensible information from OS-exposed Wi-Fi data
- Build temporal understanding of "normal" environmental conditions
- Detect deviations, anomalies, and patterns with confidence scoring
- Withstand technical, academic, and professional scrutiny

## Hard Constraints (Never Violated)

✅ **Allowed:**
- Read-only OS-level commands (netsh, ipconfig, arp)
- Environmental pattern analysis
- Temporal baseline modeling
- Aggregated statistical analysis

❌ **Prohibited:**
- Packet sniffing or monitor mode
- Deauthentication attacks
- Password cracking
- Traffic interception
- Device impersonation or spoofing
- Long-term device tracking
- Person identification
- Exact position computation

## Features

### 1. Baseline Modeling
- Learn normal Wi-Fi conditions for current location
- Track typical BSSID counts, RSSI ranges, channel usage
- Model temporal rhythms (day/night, busy/quiet periods)
- Establish statistical confidence intervals

### 2. Temporal Analysis
- Compare current state to historical observations
- Identify rising/falling trends
- Use smoothing and rolling windows
- Distinguish noise from meaningful change

### 3. Anomaly Detection
- Detect sudden spikes or drops in activity
- Identify unusual signal behavior
- Channel congestion deviations
- Confidence-scored alerts

### 4. Environmental Fingerprinting
- Create reproducible Wi-Fi environment signatures
- Compare time periods and sessions
- Fingerprint the environment, not devices
- Similarity scoring and matching

### 5. Confidence-Aware Reporting
- Every conclusion includes explanation and confidence level
- Explicit assumptions and limitations
- Relative change preferred over absolute claims
- Human and machine-readable outputs

## Architecture

```
ambient-wifi-monitor/
├── src/
│   ├── collectors/       # OS command data collection
│   ├── normalizers/      # Raw data parsing and structuring
│   ├── storage/          # Data persistence layer
│   ├── analysis/         # Analytical engines
│   │   ├── baseline.py   # Baseline modeling
│   │   ├── temporal.py   # Temporal analysis
│   │   ├── anomaly.py    # Anomaly detection
│   │   └── fingerprint.py # Environmental fingerprinting
│   ├── reporting/        # Report generation
│   └── utils/            # Shared utilities
├── data/                 # Data storage (gitignored)
│   ├── raw/             # Raw OS outputs
│   ├── normalized/      # Structured data
│   ├── baselines/       # Baseline models
│   └── reports/         # Generated reports
├── logs/                # Application logs
├── config.yaml          # Configuration
└── main.py             # CLI entry point
```

## Installation

### Prerequisites
- Python 3.9 or higher
- Windows OS (current version)
- Administrator privileges (for netsh commands)

### Setup

```powershell
# Clone repository
git clone <repository-url>
cd ambient-wifi-monitor

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Single Scan and Analysis
```powershell
python main.py scan
```

### Continuous Monitoring
```powershell
python main.py monitor --interval 60
```

### View Current Status
```powershell
python main.py status
```

### Generate Report
```powershell
python main.py report --format json
```

### View Baseline
```powershell
python main.py baseline --show
```

## Data Handling

- **Raw Data:** All OS command outputs are stored timestamped for traceability
- **Normalized Data:** Structured JSON/CSV for analysis
- **MAC Addresses:** Only as exposed by OS; never used for long-term tracking
- **Focus:** Aggregation, distributions, and trends
- **Retention:** Configurable (default: 90 days)

## Output Examples

### Human-Readable Summary
```
=== Wi-Fi Environmental Analysis ===
Timestamp: 2026-01-08 14:35:22
Observation #147

Environmental Status: NORMAL (confidence: 0.92)
  - Activity level: Within baseline range
  - Signal source diversity: 18 BSSIDs detected
  - RSSI distribution: Stable (σ = 8.2 dBm)
  - Channel usage: Moderate congestion on 2.4 GHz

Temporal Trends:
  - Short-term (10 obs): Slight decrease in activity (-8%)
  - Medium-term (50 obs): Stable
  - Long-term (200 obs): Seasonal pattern detected

Anomalies: None detected

Environmental Fingerprint: 7a4f2e9c (87% match to baseline)
```

### Machine-Readable JSON
```json
{
  "timestamp": "2026-01-08T14:35:22",
  "observation_id": 147,
  "status": "NORMAL",
  "confidence": 0.92,
  "metrics": {
    "bssid_count": 18,
    "rssi_mean": -68.4,
    "rssi_std": 8.2
  },
  "anomalies": [],
  "fingerprint": "7a4f2e9c"
}
```

## Configuration

Edit `config.yaml` to customize:
- Scan intervals
- Baseline parameters
- Anomaly thresholds
- Reporting verbosity
- Data retention

## Future Roadmap

Designed for (not yet implemented):
- External sensors (ESP32) as additional collectors
- Multi-location comparison
- Visualization dashboards
- Long-term aggregation and ML-based pattern recognition

## Ethics and Compliance

This tool is designed for:
- Personal environmental awareness
- Research and education
- Security posture assessment of your own environment

It must **never** be used for:
- Unauthorized network access
- Privacy invasion
- Device or person tracking
- Any illegal activity

## License

[To be determined - recommend permissive license with ethical use clause]

## Contributing

Contributions welcome, but must maintain:
- Ethical boundaries
- Code quality standards
- Architectural consistency
- Comprehensive testing

## Support

This is a serious analytical instrument. Questions and issues should demonstrate understanding of the tool's purpose and constraints.

---

**Remember:** This tool analyzes the Wi-Fi environment as an aggregate signal, not individual devices or people.
