```powershell
param (
    [string]$ConfigPath = "configs/audit_config.yaml"
)

Write-Host "[Audit] Starting run..."

# Activate venv if exists
if (Test-Path ".venv/Scripts/Activate.ps1") {
    . .venv/Scripts/Activate.ps1
}

# Run audit
python -c "
import yaml
from audit_probes.cyber_audit import audit_repository
from audit_probes.cloud_probe import probe
from audit_probes.telemetry_pipeline import build_dashboard_frame

with open('$ConfigPath', 'r') as f:
    config = yaml.safe_load(f)

target = config['audit']['target_path']

print('[Audit] Running cyber audit...')
audit_repository(target)

print('[Audit] Running cloud probe...')
probe(target)

print('[Audit] Running telemetry pipeline...')
build_dashboard_frame(config['telemetry']['sample_file'])
"

Write-Host "[Audit] Completed."
```
