# Ambient Wi-Fi Monitor - Development and Testing Guide

## Project Structure

```
ambient-wifi-monitor/
├── main.py                    # CLI entry point
├── config.yaml                # Configuration
├── requirements.txt           # Python dependencies
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
├── .gitignore                 # Git ignore rules
│
├── src/                       # Source code
│   ├── __init__.py           # Package initialization
│   ├── utils/                # Utilities
│   │   └── __init__.py       # Logging, config, compliance
│   ├── collectors/           # Data collection
│   │   └── __init__.py       # OS command executors
│   ├── normalizers/          # Data normalization
│   │   └── __init__.py       # Parsers for OS outputs
│   ├── storage/              # Data persistence
│   │   └── __init__.py       # Storage orchestration
│   ├── analysis/             # Analytical engines
│   │   ├── __init__.py       # Analysis module exports
│   │   ├── baseline.py       # Baseline modeling
│   │   ├── temporal.py       # Temporal analysis
│   │   ├── anomaly.py        # Anomaly detection
│   │   └── fingerprint.py    # Environmental fingerprinting
│   └── reporting/            # Report generation
│       └── __init__.py       # Text and JSON reports
│
├── data/                      # Data directory (gitignored)
│   ├── raw/                  # Raw OS outputs
│   ├── normalized/           # Structured data
│   ├── baselines/            # Baseline models
│   └── reports/              # Generated reports
│
└── logs/                      # Application logs (gitignored)
```

## Testing the Application

### Step 1: Installation
```powershell
# Navigate to project directory
cd c:\Users\admin\Documents\GitHub\local-wifi-observer

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Initial Configuration
The default `config.yaml` is ready to use. For faster testing, you may want to reduce the minimum baseline observations:

```yaml
baseline:
  min_observations: 20  # Reduced from 100 for testing
```

### Step 3: First Scan
```powershell
# Run as Administrator (required for netsh commands)
python main.py scan
```

Expected output:
- Data collection from netsh, ipconfig, arp
- Normalization of raw data
- Analysis (no baseline yet)
- Text report

### Step 4: Build Baseline
```powershell
# Run continuous monitoring to build baseline
python main.py monitor --interval 30 --count 25
```

This will:
- Collect 25 observations (30 seconds apart)
- Automatically build baseline after reaching min_observations
- Generate reports for each scan

### Step 5: Check Status
```powershell
python main.py status
```

### Step 6: View Baseline
```powershell
python main.py baseline --show
```

### Step 7: Continue Monitoring
```powershell
# Monitor with baseline active
python main.py monitor --interval 60
```

## Development Tasks

### Adding New Features

1. **New Collector**: Add to `src/collectors/__init__.py`
2. **New Normalizer**: Add to `src/normalizers/__init__.py`
3. **New Analysis**: Create new file in `src/analysis/`
4. **New Report Format**: Add generator to `src/reporting/__init__.py`

### Configuration Customization

Edit `config.yaml` to adjust:
- **Collection frequency**: `collection.scan_interval`
- **Baseline sensitivity**: `baseline.min_observations`, `baseline.stability_threshold`
- **Anomaly detection**: `anomaly.zscore_threshold`, `anomaly.method`
- **Report verbosity**: `reporting.verbosity` (minimal, standard, detailed)

### Logging

Logs are written to `logs/ambient-wifi-monitor.log` by default.

Adjust logging level in `config.yaml`:
```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Advanced Usage

### Manual Baseline Creation
```python
from src.utils import load_config
from src.storage import StorageOrchestrator
from src.analysis import BaselineModel

config = load_config()
storage = StorageOrchestrator(config)
baseline_model = BaselineModel(config)

# Load historical observations
observations = storage.normalized_store.load_recent(100)

# Build baseline
baseline = baseline_model.build(observations)

# Save baseline
storage.baseline_store.save(baseline, 'custom_baseline')
```

### Data Analysis
All normalized data is stored as JSON in `data/normalized/`.
BSSID history is also exported to CSV: `data/normalized/bssids_history.csv`.

You can analyze this data with pandas:
```python
import pandas as pd

df = pd.read_csv('data/normalized/bssids_history.csv')
print(df.describe())
```

### Custom Reports
Create custom analysis by loading observations:
```python
from src.storage import StorageOrchestrator
from src.utils import load_config

config = load_config()
storage = StorageOrchestrator(config)

# Load recent observations
recent = storage.normalized_store.load_recent(10)

# Analyze as needed
for obs in recent:
    networks = obs.get('wlan_networks', {})
    print(f"BSSIDs: {networks.get('summary', {}).get('bssid_count', 0)}")
```

## Performance Considerations

- **Scan interval**: 60 seconds is recommended for normal operation
- **Data retention**: Configure in `config.yaml` (default: 90 days)
- **Baseline updates**: Every 10 observations by default
- **Memory usage**: Minimal (only recent observations loaded into memory)

## Troubleshooting

### Issue: "netsh command failed"
**Solution**: Run PowerShell as Administrator

### Issue: No baseline created
**Solution**: Ensure you have at least `min_observations` scans completed

### Issue: All anomalies detected
**Solution**: Baseline may need more observations for stability

### Issue: Import errors
**Solution**: Ensure virtual environment is activated and dependencies installed

## Ethics and Compliance

Every operation is validated through `ComplianceValidator`:
- Read-only operations only
- No packet sniffing
- No monitor mode
- No device tracking
- No person identification

Violations will raise `PermissionError`.

## Future Extensions

The architecture is designed for future additions:
- External sensor integration (ESP32)
- Multi-location comparison
- Web dashboard
- Machine learning models
- Long-term pattern recognition

## Contributing

When contributing, maintain:
- Modular architecture
- Clear separation of concerns
- Comprehensive logging
- Ethical boundaries
- Professional code quality

## Support

This is a serious analytical instrument. Use it responsibly and within legal boundaries.
