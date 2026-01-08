# Ambient Wi-Fi Monitor - Installation Verification Script
# Run this script to verify that everything is set up correctly

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  AMBIENT WI-FI MONITOR - Installation Verification" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
    
    # Parse version
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
            Write-Host "  ⚠ Warning: Python 3.9+ recommended, you have $pythonVersion" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ✗ Python not found or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if virtual environment exists
Write-Host "Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Virtual environment not found" -ForegroundColor Yellow
    Write-Host "    Run: python -m venv venv" -ForegroundColor White
}

Write-Host ""

# Check if virtual environment is activated
Write-Host "Checking if virtual environment is activated..." -ForegroundColor Yellow
if ($env:VIRTUAL_ENV) {
    Write-Host "  ✓ Virtual environment is activated" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Virtual environment is NOT activated" -ForegroundColor Yellow
    Write-Host "    Run: .\venv\Scripts\Activate.ps1" -ForegroundColor White
}

Write-Host ""

# Check required files
Write-Host "Checking project files..." -ForegroundColor Yellow
$requiredFiles = @(
    "main.py",
    "config.yaml",
    "requirements.txt",
    "src\__init__.py",
    "src\collectors\__init__.py",
    "src\normalizers\__init__.py",
    "src\storage\__init__.py",
    "src\analysis\baseline.py",
    "src\analysis\temporal.py",
    "src\analysis\anomaly.py",
    "src\analysis\fingerprint.py",
    "src\reporting\__init__.py",
    "src\utils\__init__.py"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file - MISSING!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

Write-Host ""

# Check Python packages (if venv is activated)
if ($env:VIRTUAL_ENV) {
    Write-Host "Checking Python packages..." -ForegroundColor Yellow
    
    $requiredPackages = @("numpy", "pandas", "scipy", "statsmodels", "pyyaml")
    $installedPackages = pip list 2>&1 | Out-String
    
    foreach ($package in $requiredPackages) {
        if ($installedPackages -match $package) {
            Write-Host "  ✓ $package installed" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $package NOT installed" -ForegroundColor Red
            Write-Host "    Run: pip install -r requirements.txt" -ForegroundColor White
        }
    }
} else {
    Write-Host "Skipping package check (activate venv first)" -ForegroundColor Yellow
}

Write-Host ""

# Check Administrator privileges
Write-Host "Checking Administrator privileges..." -ForegroundColor Yellow
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Host "  ✓ Running as Administrator" -ForegroundColor Green
} else {
    Write-Host "  ⚠ NOT running as Administrator" -ForegroundColor Yellow
    Write-Host "    netsh commands require Administrator privileges" -ForegroundColor White
}

Write-Host ""

# Test netsh command
Write-Host "Testing Wi-Fi command access..." -ForegroundColor Yellow
try {
    $netshTest = netsh wlan show interfaces 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Wi-Fi commands accessible" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Wi-Fi commands may require Administrator privileges" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Error running netsh command" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan

# Summary
Write-Host ""
Write-Host "VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "--------------------" -ForegroundColor Cyan

if ($allFilesExist -and $env:VIRTUAL_ENV -and $isAdmin) {
    Write-Host "✓ All checks passed! Ready to run." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "  1. Run your first scan: python main.py scan" -ForegroundColor White
    Write-Host "  2. Build baseline: python main.py monitor --interval 30 --count 25" -ForegroundColor White
    Write-Host "  3. Start monitoring: python main.py monitor --interval 60" -ForegroundColor White
} else {
    Write-Host "⚠ Some checks failed. Please review above." -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $env:VIRTUAL_ENV) {
        Write-Host "Action required: Activate virtual environment" -ForegroundColor Yellow
        Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host ""
    }
    
    if (-not $isAdmin) {
        Write-Host "Action required: Run PowerShell as Administrator" -ForegroundColor Yellow
        Write-Host ""
    }
    
    if (-not $allFilesExist) {
        Write-Host "Action required: Some project files are missing" -ForegroundColor Yellow
        Write-Host ""
    }
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
