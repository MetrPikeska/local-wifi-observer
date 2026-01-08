# Ambient Wi-Fi Monitor - Quick Start Guide

## Installation

1. **Clone the repository:**
   ```powershell
   cd c:\Users\admin\Documents\GitHub\local-wifi-observer
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

## Basic Usage

### Single Scan
Perform one environmental scan and analysis:
```powershell
python main.py scan
```

### Continuous Monitoring
Monitor continuously with 60-second intervals:
```powershell
python main.py monitor --interval 60
```

Stop with `Ctrl+C`.

### Check Status
View system status and observation count:
```powershell
python main.py status
```

### View Baseline
Display baseline model information:
```powershell
python main.py baseline --show
```

## Understanding the Output

### Environmental Status
- **NORMAL**: Activity within expected baseline range
- **SLIGHTLY_ELEVATED/REDUCED**: Minor deviation from baseline
- **ANOMALOUS_HIGH/LOW**: Significant deviation detected

### Confidence Scores
- **0.90+**: High confidence
- **0.70-0.89**: Medium confidence
- **Below 0.70**: Lower confidence

### Anomalies
- **High severity**: Significant deviation requiring attention
- **Medium severity**: Notable but less critical deviation

## Building a Baseline

The system automatically builds a baseline after collecting 100 observations (configurable in `config.yaml`).

For faster baseline creation during initial testing:
1. Edit `config.yaml`
2. Set `baseline.min_observations` to a lower value (e.g., 20)
3. Run continuous monitoring for sufficient observations

## Configuration

Edit `config.yaml` to customize:
- Scan intervals
- Baseline parameters
- Anomaly detection thresholds
- Reporting verbosity
- Data retention

## Data Storage

All data is stored in the `data/` directory:
- `raw/`: Raw OS command outputs
- `normalized/`: Structured JSON data
- `baselines/`: Baseline models
- `reports/`: Generated reports

## Troubleshooting

### "Command failed" errors
Run PowerShell as Administrator. The `netsh wlan` commands require elevated privileges.

### Insufficient baseline data
Continue monitoring until you reach the minimum observation count (check with `python main.py status`).

### No Wi-Fi adapter
Ensure your Windows laptop has an active Wi-Fi adapter.

## Ethical Reminders

This tool:
- ✅ Analyzes environmental Wi-Fi signals (read-only)
- ❌ Does NOT crack passwords
- ❌ Does NOT intercept traffic
- ❌ Does NOT track specific devices
- ❌ Does NOT identify people

Use responsibly and legally.
