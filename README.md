# Audit Probes

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20204042.svg)](https://doi.org/10.5281/zenodo.20204042)

**Stress-testing systemic friction and bridging observability gaps within mission-critical infrastructures.**

**Audit Probes** is an intentionally minimal research- and open-source instrumentation toolkit organized around three modules: `cyber_audit`, `telemetry_pipeline`, and `cloud_probe`. Its purpose is not to present a production-ready platform, but to show reproducible technical work across software assurance, telemetry handling, and infrastructure measurement.

The emphasis throughout is on:

- traceability
- reproducibility
- clarity of reasoning
- explicit limitations

Automation was used only for non-critical scaffolding and boilerplate support. Core logic, assumptions, error handling, and outputs were manually reviewed.

## Modules

### Cyber Audit [Provenance Attestation](./src/audit_probes/cyber_audit)

**Focus:** Detailed logic for automated auditing and dependency risk.<br>
**Friction:** Onboarding ambiguity, open-source software supply chain opacity, configuration risk, and lack of cryptographic provenance in CI/CD.<br>
**Key initiative:** Secret detection and dependency risk scoring.<br>
**Documentation:** [Cyber Audit](./src/audit_probes/cyber_audit/README.md)<br>
**Relevant script:** [cyber_audit.py](./src/audit_probes/cyber_audit/cyber_audit.py)

### Telemetry Pipeline [Signal Diagnostic in Space Systems](./src/audit_probes/telemetry_pipeline)

**Focus:** Telemetry standardization and validation under noise.<br>
**Friction:** Noisy, incomplete, non-standard telemetry.<br>
**Key Initiative:** Assumption-explicit visualization and evaluation layers of orbital data.<br>
**Documentation:** [Telemetry Pipeline](./src/audit_probes/telemetry_pipeline/README.md)<br>
**Relevant script:** [telemetry_pipeline.py](./src/audit_probes/telemetry_pipeline/telemetry_pipeline.py)

### Cloud Probe [API Infra Probe](./src/audit_probes/cloud_probe)

**Focus:** Basic API and endpoint probing to approach cloud and AI infrastructure with observable data.<br>
**Friction:** Black-box abstractions and unverifiable performance claims.<br>
**Key Initiative:** External latency probing and consistency metrics.<br>
**Documentation:** [Cloud Probe](./src/audit_probes/cloud_probe/README.md)<br>
**Relevant script:** [cloud_probe.py](./src/audit_probes/cloud_probe/cloud_probe.py)

**Each module contains a dedicated Technical Note covering specific methodologies and limitations.**

---

## Development

Install local development tools with:

```bash
pip install -e ".[dev]"
```

Run the validation suite from the repository root with:

```bash
PYTHONPATH=src python -m pytest
```

### Methodology [Logic](./docs/METHODOLOGY.md)
### Notes [Theoretical Background](./docs/NOTES.md)
### Verification [Limitations](./docs/VERIFICATION.md)

## Citation

This repository is archived through the Zenodo-GitHub integration. Use the DOI
below in the arXiv submission `Code` field.

```bibtex
@software{lee_audit_probes_2026,
  author = {Lee, L. S.},
  title = {Audit Probes},
  year = {2026},
  version = {0.1.2},
  license = {MIT},
  url = {https://github.com/intelligentiaomni/audit-probes},
  doi = {10.5281/zenodo.20178117}
}
```

Preferred citation metadata is also provided in [`CITATION.cff`](./CITATION.cff).
