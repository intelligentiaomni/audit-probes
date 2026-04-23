## Cyber Audit

Target: Cybercampus Sverige Junior Infrastructure Support 

### Purpose

`cyber_audit` is a lightweight repository-audit module for investigating practical security review in an open-source technical setting. It automates a first-pass scan for possible exposed secrets, dependency version risks, and unsafe environment-variable usage.

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