## Telemetry Pipeline

Target: KTH Space Center / ORBIT-oriented telemetry investigation

### Purpose

`telemetry_pipeline` is a minimal, reproducible data-processing module for working with public telemetry-style datasets. It was built to explore how noisy orbital or suborbital data can be cleaned and visualized without hiding the assumptions that shape the result.

The goal is not only to produce a readable plot, but to keep the analysis scientifically honest when values are missing, filtered, or interpolated.

### Tech Stack

- Python 3.11
- `pandas` for ingestion and cleaning
- `matplotlib` for visualization
- Codex assistance for boilerplate structure
- manual review of anomaly logic, interpolation assumptions, and output behavior

The module is designed to stay explicit about where data has been interpolated and where anomaly flags are introduced.

### Reproducibility

Run locally with:

```bash
git clone https://github.com/intelligentiaomni/audit-probes
cd audit-probes
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
python -c "from audit_probes.telemetry_pipeline import build_dashboard_frame; print(build_dashboard_frame('data/samples/esa_sample.json')[['time','altitude','anomaly_flag']])"
```

A fixed sample dataset is included so the pipeline can be run without external APIs or live telemetry feeds.

### Methodology

The pipeline follows a simple, inspectable flow:

- ingest telemetry from CSV or JSON
- remove invalid or non-physical values
- interpolate missing altitude values
- flag abrupt jumps as anomalies
- generate a basic altitude profile

This design favors transparency and repeatability over model complexity.

### Limitations

- cleaning via simple thresholds may introduce bias
- interpolation is an analytical assumption, not a measured observation
- the sample workflow is exploratory and not intended for mission-critical telemetry analysis