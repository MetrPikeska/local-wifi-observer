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

### Quick Start Commands

```powershell
# 1. Single scan - basic environmental snapshot
python main.py scan

# 2. View current system status
python main.py status

# 3. Generate detailed text report
python main.py report

# 4. Generate JSON report for machine processing
python main.py report --format json

# 5. View current baseline statistics
python main.py baseline --show

# 6. Continuous monitoring (60 second intervals)
python main.py monitor --interval 60

# 7. Continuous monitoring (5 minute intervals)
python main.py monitor --interval 300
```

### Command Reference

#### `scan` - Single Environmental Scan
Performs one complete data collection cycle including:
- Wi-Fi interface status
- Available networks (BSSIDs, SSIDs, channels, RSSI)
- Network configuration (IP, gateways)
- ARP table snapshot
- Statistical analysis
- Anomaly detection
- Fingerprint generation

```powershell
python main.py scan
```

**Output:**
- Raw data saved to `data/raw/`
- Normalized data saved to `data/normalized/`
- Text report saved to `data/reports/`
- JSON report saved to `data/reports/`
- Console summary displayed

---

#### `monitor` - Continuous Monitoring
Runs repeated scans at specified intervals, ideal for:
- Long-term pattern observation
- Baseline building
- Change detection over time

```powershell
# Monitor every 60 seconds
python main.py monitor --interval 60

# Monitor every 5 minutes (300 seconds)
python main.py monitor --interval 300

# Monitor every hour (3600 seconds)
python main.py monitor --interval 3600
```

**Options:**
- `--interval`: Seconds between scans (default: 60)

**Press Ctrl+C to stop monitoring**

---

#### `status` - System Status Check
Quick health check showing:
- Total observations collected
- Date range of data
- Baseline status
- Recent activity summary

```powershell
python main.py status
```

**Use this to:**
- Verify system is working
- Check data collection progress
- See baseline readiness

---

#### `report` - Generate Analysis Report
Creates comprehensive report from latest observation:
- Environmental metrics
- Baseline comparison
- Temporal trends
- Anomalies detected
- Distance estimation (if enabled)
- Fingerprint analysis

```powershell
# Human-readable text report
python main.py report

# Machine-readable JSON report
python main.py report --format json

# Both formats
python main.py report --format text
python main.py report --format json
```

**Output locations:**
- Text: `data/reports/report_YYYYMMDD_HHMMSS.txt`
- JSON: `data/reports/report_YYYYMMDD_HHMMSS.json`

---

#### `baseline` - Baseline Management
View or rebuild baseline statistical model:

```powershell
# Show current baseline statistics
python main.py baseline --show

# Rebuild baseline from collected data
python main.py baseline --rebuild
```

**Baseline includes:**
- BSSID count (mean, std, confidence intervals)
- RSSI distribution (mean, std, percentiles)
- Channel usage patterns
- Temporal patterns (hour-of-day, day-of-week)

---

### Typical Workflows

#### First Time Setup
```powershell
# 1. Run initial scan
python main.py scan

# 2. Check status
python main.py status

# 3. View report
python main.py report
```

#### Building Baseline (Recommended)
```powershell
# Run monitoring for 24-48 hours to learn environment
python main.py monitor --interval 300

# After sufficient data, view baseline
python main.py baseline --show
```

#### Daily Analysis
```powershell
# Morning scan
python main.py scan

# Check for anomalies
python main.py report

# Compare to baseline
python main.py baseline --show
```

#### Investigating Changes
```powershell
# Take current snapshot
python main.py scan

# Compare to historical data
python main.py report --format json

# Look for patterns
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
