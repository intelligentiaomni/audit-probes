## Cloud Probe

Target: Stockholm Tech Show / cloud and AI infrastructure observability

### Purpose

`cloud_probe` is a lightweight probing module for measuring API latency and response consistency across repeated requests. It was built to explore infrastructure behavior empirically rather than relying only on vendor claims or static documentation.

The aim is to provide a minimal, inspectable measurement tool that supports systems thinking and basic observability.

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

The probe records a limited set of observable signals:

- HTTP status code
- response latency
- payload size
- repeated-response fingerprint consistency

This keeps the module simple enough to inspect directly, while still being useful for quick infrastructure checks.

### Limitations

- latency is measured without network normalization
- results are affected by normal network variance
- the probe is a lightweight interrogative tool, not a substitute for full observability infrastructure