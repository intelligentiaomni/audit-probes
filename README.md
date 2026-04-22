# Audit Probes

Audit Probes is a small research-open-source instrumentation toolkit organized around three modules: `cyber_audit`, `telemetry_pipeline`, and `cloud_probe`. The project is intentionally lightweight. Its purpose is not to present a production-ready platform, but to show reproducible technical work across software assurance, telemetry handling, and infrastructure measurement.

The emphasis throughout is on:

- traceability
- reproducibility
- clarity of reasoning
- explicit limits

Automation was used only for non-critical scaffolding and boilerplate support. Core logic, assumptions, error handling, and outputs were manually reviewed.

## Cyber Audit

Target: Cybercampus Sverige Junior Infrastructure Support application

### Purpose

`cyber_audit` is a lightweight repository-audit module for exploring practical security review in an open-source setting. It automates a first-pass scan for possible exposed secrets, dependency version risks, and unsafe environment-variable usage.

The aim is not to replace a full security assessment, but to show a traceable workflow between manual review and Python-based automation.

### Stack

- Python 3.11
- standard-library scanning and JSON logging
- Codex assistance for boilerplate structure and test scaffolding
- manual review of core logic, defensive handling, and audit assumptions

Defensive logic was added so the tool remains stable on empty inputs, unreadable files, and incomplete repository data.

More specifically, the audit uses defensive error handling so the scan remains stable when individual files are unreadable, oddly encoded, or malformed. Instead of crashing on partial repository issues, it skips or records those failures and continues, preserving a reproducible first-pass result.

### Reproducibility

Run locally with:

```bash
git clone https://github.com/intelligentiaomni/audit-probes
cd audit-probes
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
python -c "from audit_probes.cyber_audit import audit_repository; print(audit_repository('[sample-path]'))"
```

A fixed sample input can be used to inspect output without external credentials or API access.

### Method

The audit uses simple, inspectable rules rather than opaque heuristics. Current checks include:

- string-based matching for possible secrets
- lightweight dependency version inspection
- detection of unsafe environment-variable access patterns

This design favors readability and reproducibility over broad coverage.

### Limitations

- secret detection is based on string matching, not semantic analysis
- the scanner may produce false positives
- dependency checks are heuristic and do not replace a full vulnerability database workflow

## Telemetry Pipeline

Target: KTH Space Center / ORBIT-oriented telemetry exploration

### Purpose

`telemetry_pipeline` is a small, reproducible data-processing module for working with public telemetry-style datasets. It was built to explore how noisy orbital or suborbital data can be cleaned and visualized without hiding the assumptions that shape the result.

The goal is not only to produce a readable plot, but to keep the analysis scientifically honest when values are missing, filtered, or interpolated.

### Stack

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

### Method

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

## Cloud Probe

Target: Stockholm Tech Show / cloud and AI infrastructure observability

### Purpose

`cloud_probe` is a lightweight probing module for measuring API latency and response consistency across repeated requests. It was built to explore infrastructure behavior empirically rather than relying only on vendor claims or static documentation.

The aim is to provide a small, inspectable measurement tool that supports systems thinking and basic observability.

### Stack

- Python 3.11
- `requests` for HTTP probing
- standard-library timing and hashing utilities
- Codex assistance for boilerplate structure and test scaffolding
- manual review of request handling, failure behavior, and result reporting

Defensive logic is included so failed requests return structured output rather than crashing the probe.

### Reproducibility

Run locally with:

```bash
git clone https://github.com/intelligentiaomni/audit-probes
cd audit-probes
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
python -c "from audit_probes.cloud_probe import probe_consistency; print(probe_consistency('https://example.com', attempts=3))"
```

Given a fixed endpoint and a fixed number of attempts, the script produces bounded and inspectable output.

### Method

The probe records a small set of observable signals:

- HTTP status code
- response latency
- payload size
- repeated-response fingerprint consistency

This keeps the module simple enough to inspect directly while still being useful for quick infrastructure checks.

### Limitations

- latency is measured without network normalization
- results are affected by normal network variance
- the probe is a lightweight exploratory tool, not a substitute for full observability infrastructure
