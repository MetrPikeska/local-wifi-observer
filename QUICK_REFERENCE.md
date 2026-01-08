# 🎯 AMBIENT WI-FI MONITOR - QUICK REFERENCE CARD

## 📦 INSTALLATION (First Time Only)
```powershell
cd c:\Users\admin\Documents\GitHub\local-wifi-observer
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🚀 COMMON COMMANDS

### Single Scan
```powershell
python main.py scan
```
*Performs one scan, shows results, saves data*

### Start Monitoring (Recommended)
```powershell
python main.py monitor --interval 60
```
*Continuous monitoring, 60-second intervals, Ctrl+C to stop*

### Build Initial Baseline (First Time)
```powershell
python main.py monitor --interval 30 --count 25
```
*Collect 25 observations to establish baseline (faster interval for testing)*

### Check System Status
```powershell
python main.py status
```
*Shows observation count, baseline status*

### View Baseline Details
```powershell
python main.py baseline --show
```
*Display baseline statistics and metrics*

## 📊 UNDERSTANDING OUTPUT

### Environmental Status
| Status | Meaning |
|--------|---------|
| `NORMAL` | Within baseline range (good) |
| `SLIGHTLY_ELEVATED` | Minor increase detected |
| `SLIGHTLY_REDUCED` | Minor decrease detected |
| `ANOMALOUS_HIGH` | Significant spike detected |
| `ANOMALOUS_LOW` | Significant drop detected |
| `NO_BASELINE` | Not enough data yet |

### Confidence Levels
| Range | Interpretation |
|-------|----------------|
| 0.90+ | High confidence - reliable result |
| 0.70-0.89 | Medium confidence - probable result |
| 0.50-0.69 | Low confidence - provisional result |
| < 0.50 | Very low confidence - need more data |

### Anomaly Severity
| Level | Meaning | Action |
|-------|---------|--------|
| `HIGH` | Significant deviation | Investigate |
| `MEDIUM` | Notable but less critical | Monitor |
| `None` | Normal operation | Continue |

## 📁 DATA LOCATIONS

```
local-wifi-observer/
├── data/
│   ├── raw/              ← Raw OS command outputs
│   ├── normalized/       ← Structured JSON data
│   │   └── bssids_history.csv  ← Easy to analyze
│   ├── baselines/        ← Baseline models
│   └── reports/          ← Generated reports
└── logs/
    └── ambient-wifi-monitor.log  ← Application logs
```

## 🔧 QUICK CONFIGURATION TWEAKS

### Edit config.yaml for:

**Faster Baseline (Testing)**
```yaml
baseline:
  min_observations: 20  # Default: 100
```

**Change Scan Interval**
```yaml
collection:
  scan_interval: 30  # Default: 60 seconds
```

**More Detailed Reports**
```yaml
reporting:
  verbosity: "detailed"  # Options: minimal, standard, detailed
```

**Debug Logging**
```yaml
logging:
  level: "DEBUG"  # Options: DEBUG, INFO, WARNING, ERROR
```

## 📈 TYPICAL WORKFLOW

1. **Day 1: Initial Setup**
   - Install (one time)
   - Run monitor for 1-2 hours to build baseline
   - Review baseline: `python main.py baseline --show`

2. **Day 2+: Regular Monitoring**
   - Run `python main.py monitor --interval 60`
   - Let it run in background
   - Check reports in `data/reports/`

3. **When Anomalies Detected**
   - Review the anomaly description
   - Check what changed in environment
   - Decide if it's expected or investigate

## 🛠️ TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "Access Denied" | Run PowerShell as Administrator |
| "Command failed" | Ensure Wi-Fi adapter is enabled |
| "No baseline" | Need more observations (run monitor) |
| Import errors | Activate venv: `.\venv\Scripts\Activate.ps1` |
| All anomalies | Baseline may be unstable, collect more data |

## 💡 PRO TIPS

✅ **Run as Administrator** - Required for netsh commands

✅ **Let baseline stabilize** - 100+ observations gives best results

✅ **Use consistent intervals** - 60 seconds is good for most cases

✅ **Monitor during normal use** - Don't move laptop while building baseline

✅ **Check logs** - `logs/ambient-wifi-monitor.log` has detailed info

✅ **Export CSV data** - `data/normalized/bssids_history.csv` for Excel/pandas

## 🎓 WHAT THIS TOOL DOES

✅ Monitors Wi-Fi environment around your laptop
✅ Learns what's "normal" for your location
✅ Detects unusual changes and patterns
✅ Creates environmental fingerprints
✅ Generates professional reports

## ⛔ WHAT THIS TOOL DOES NOT DO

❌ Crack passwords
❌ Intercept traffic
❌ Track specific devices
❌ Identify people
❌ Attack networks
❌ Access unauthorized data

## 📞 GETTING HELP

1. Check `QUICKSTART.md` for basic usage
2. Review `DEVELOPMENT.md` for advanced features
3. Read `ARCHITECTURE.md` for system design
4. Check logs in `logs/` directory
5. Review `PROJECT_SUMMARY.md` for complete overview

## 📖 KEY CONCEPTS

**Baseline**: Statistical model of "normal" Wi-Fi conditions for your location

**BSSID**: Unique identifier for each access point (like a MAC address)

**Observation**: One complete scan of the Wi-Fi environment

**Fingerprint**: Unique signature identifying Wi-Fi environment state

**Temporal Analysis**: Comparing current state to historical patterns

**Anomaly**: Detected deviation from expected baseline behavior

---

## 🎯 TYPICAL OUTPUT EXAMPLE

```
======================================================================
Wi-Fi Environmental Analysis Report
======================================================================

Timestamp: 2026-01-08 14:35:22
Observation: #147

ENVIRONMENTAL STATUS
----------------------------------------------------------------------
Status: NORMAL (confidence: 0.92)
  - Activity level: 18 BSSIDs detected
  - Baseline average: 17.3 BSSIDs
  - Deviation: +4.0%

TEMPORAL TRENDS
----------------------------------------------------------------------
Short-term: Stable | Medium-term: Stable

ANOMALY DETECTION
----------------------------------------------------------------------
No anomalies detected

ENVIRONMENTAL FINGERPRINT
----------------------------------------------------------------------
Fingerprint: 7a4f2e9c
Match to baseline: 87.5%
```

---

**Remember: This is environmental sensing, not network hacking.**
**Use ethically and legally. Monitor your own environment only.**

---

*Quick Reference v1.0 - Ambient Wi-Fi Monitor*
