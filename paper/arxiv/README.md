# arXiv Preparation Notes

This directory contains a draft arXiv source package for the Audit Probes
technical report.

## Candidate Metadata

- Title: Cross-Domain Audit Probes: Minimal Instrumentation for Reproducible Systemic-Risk Interrogation
- Suggested primary category: `cs.SE`
- Possible cross-list: `cs.CR` if the final abstract emphasizes security assurance and audit evidence.
- Avoid `cs.CY` unless the final manuscript adds a substantive policy, legal, educational, or social-impact contribution.
- Format: LaTeX source preferred
- Main file: `audit_probes_technical_report.tex`
- Code field: `https://doi.org/10.5281/zenodo.20178117`

## Submission Checks

- Keep file names ASCII and case-stable.
- Use TeX/LaTeX source rather than a PDF generated from TeX.
- Submit the LaTeX source package, not only the generated PDF.
- Do not submit Mermaid diagrams directly; compile diagrams as native LaTeX/TikZ or PDF/PNG figures.
- Include every required figure file if external figures are introduced.
- Keep figure references relative to this source directory, for example `figures/telemetry_baseline_v010.png`.
- Verify title, abstract, author, category, license, and repository URL before submission.
- Confirm the final Zenodo DOI is entered in the arXiv `Code` field: `https://doi.org/10.5281/zenodo.20178117`.
- Confirm any KTH-adjacent or access-gated target has permission, commit hash, license, and audit scope before citing it as evidence.
- For visibility planning, prefer a Wednesday or Thursday submission before 14:00 ET when the paper is otherwise ready.

## Current Status

This is a draft manuscript source package prepared for arXiv review. It has
been consolidated from the longer technical-report draft by keeping verified
repository metrics as results and moving unsupported agentic/cryptographic
claims into the roadmap. The TeX has been compiled locally; before submission,
review the resulting PDF for layout, category fit, and moderation risk.

The citation and name-reference list has not yet been fully updated or
rechecked. Before submission, verify every reference, URL, access date, author
name, and in-text citation against the final claims.
