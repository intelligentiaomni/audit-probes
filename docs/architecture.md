## System Architecture Map

```text
audit-probes/
|-- configs/
|-- schemas/                         # data definitions for observability and validation
|   |-- cyber_audit.schema.json
|   |-- telemetry_pipeline.json
|   `-- cloud_probe.schema.json
|-- src/
|   |-- audit_probes/                 # instrumentation
|   |-- collectors/                   # data ingestion and normalization
|   `-- logic/                        # core utilities
|-- results/                          # audit output artifacts
|-- runs/                             # execution records
|-- docs/
|   `-- METHODOLOGY.md                # scientific contract of system
|-- data/                             # inputs, datasets, and targets
|-- tests/
|-- run-audit.ps1                     # local execution harness
|-- pyproject.toml
`-- validator.py                      # integrity layer
```
