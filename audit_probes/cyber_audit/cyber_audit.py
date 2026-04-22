"""Security audit helpers for lightweight repository reviews."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None


SECRET_RULES = (
    (
        "hardcoded_secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][^'\"]{6,}['\"]"
        ),
        "high",
        "Possible hard-coded secret assignment",
    ),
    (
        "secret_keyword",
        re.compile(r"(?i)\b(?:API_KEY|SECRET|TOKEN|PASSWORD)\b"),
        "medium",
        "Secret-related token present in source",
    ),
)

ENV_RULES = (
    (
        "env_without_default",
        re.compile(r"os\.getenv\(\s*['\"][A-Z0-9_]+['\"]\s*\)"),
        "medium",
        "Environment variable read without a default value",
    ),
    (
        "env_without_guard",
        re.compile(r"os\.environ\[\s*['\"][A-Z0-9_]+['\"]\s*\]"),
        "medium",
        "Environment variable accessed directly; missing keys may crash execution",
    ),
)

DEPENDENCY_BASELINES = {
    "django": "4.2",
    "flask": "2.3",
    "github.com/go-git/go-git/v5": "5.18.0",
    "github.com/rogpeppe/go-internal": "1.14.1",
    "jinja2": "3.1",
    "pandas": "2.0",
    "pyyaml": "6.0",
    "requests": "2.31",
    "go.yaml.in/yaml/v3": "3.0.4",
    "golang.org/x/mod": "0.35.0",
    "golang.org/x/tools": "0.44.0",
    "golang.org/x/vuln": "1.1.4",
    "urllib3": "2.0",
}

SAFE_SECRET_PATTERNS = (
    re.compile(r"\${{\s*github\.token\s*}}", re.IGNORECASE),
    re.compile(r"\bautomation-token\b", re.IGNORECASE),
    re.compile(r"create-github-app-token", re.IGNORECASE),
    re.compile(r"^\s*-\s*name:\s+.*\btoken\b", re.IGNORECASE),
    re.compile(r'["\']path["\']\s*:\s*["\'][^"\']+/token["\']', re.IGNORECASE),
)

TEXT_EXTENSIONS = {
    ".cfg",
    ".conf",
    ".env",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".pyi",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

DEPENDENCY_FILES = {"go.mod", "pyproject.toml", "requirements.txt", "requirements-dev.txt"}


@dataclass(frozen=True)
class AuditFinding:
    category: str
    file: str
    line: int
    severity: str
    match: str
    detail: str


def scan_for_secrets(path: str | os.PathLike[str]) -> list[tuple[str, str]]:
    """Compatibility wrapper mirroring the minimal hook in the project notes."""
    findings = []
    seen = set()
    for finding in _scan_text_rules(Path(path), SECRET_RULES):
        key = (finding.file, finding.match)
        if key in seen:
            continue
        seen.add(key)
        findings.append(key)
    return findings


def audit_repository(
    path: str | os.PathLike[str], output_path: str | os.PathLike[str] | None = None
) -> dict[str, object]:
    """Run all available repository checks and optionally persist a JSON log."""
    root = Path(path).resolve()
    findings = []
    errors = []

    for scanner in (lambda: _scan_text_rules(root, SECRET_RULES), lambda: _scan_dependency_files(root), lambda: _scan_text_rules(root, ENV_RULES)):
        try:
            findings.extend(scanner())
        except OSError as exc:
            errors.append(str(exc))

    findings = sorted(
        findings,
        key=lambda item: (item.category, item.file, item.line, item.match),
    )
    report = {
        "target": str(root),
        "summary": {
            "findings": len(findings),
            "high": sum(1 for item in findings if item.severity == "high"),
            "medium": sum(1 for item in findings if item.severity == "medium"),
            "low": sum(1 for item in findings if item.severity == "low"),
            "errors": len(errors),
        },
        "findings": [asdict(item) for item in findings],
        "errors": errors,
    }

    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def _scan_text_rules(root: Path, rules: tuple[tuple[str, re.Pattern[str], str, str], ...]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for file_path in _iter_candidate_files(root):
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            for category, pattern, severity, detail in rules:
                if pattern.search(line) and not _should_ignore_secret_line(category, line):
                    findings.append(
                        AuditFinding(
                            category=category,
                            file=str(file_path.relative_to(root)),
                            line=line_number,
                            severity=severity,
                            match=line.strip()[:160],
                            detail=detail,
                        )
                    )
    return findings


def _scan_dependency_files(root: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for file_path in root.rglob("*"):
        if not file_path.is_file() or file_path.name not in DEPENDENCY_FILES:
            continue

        if file_path.name == "go.mod":
            findings.extend(_scan_go_mod(file_path, root))
        elif file_path.name == "pyproject.toml":
            findings.extend(_scan_pyproject(file_path, root))
        else:
            findings.extend(_scan_requirements(file_path, root))
    return findings


def _scan_go_mod(file_path: Path, root: Path) -> list[AuditFinding]:
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    dependencies: list[tuple[int, str, str]] = []
    findings: list[AuditFinding] = []
    in_require_block = False

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        if line == "require (":
            in_require_block = True
            continue
        if in_require_block and line == ")":
            in_require_block = False
            continue
        if line.startswith("replace ") and " => " in line:
            finding = AuditFinding(
                category="replace_directive",
                file=str(file_path.relative_to(root)),
                line=line_number,
                severity="medium",
                match=line,
                detail="Go module replace directive can hide dependency provenance changes",
            )
            if re.search(r"=>\s*(?:\.{1,2}[\\/]|[A-Za-z]:[\\/]|/)", line):
                finding = AuditFinding(
                    category="local_replace_directive",
                    file=str(file_path.relative_to(root)),
                    line=line_number,
                    severity="medium",
                    match=line,
                    detail="Go module replace directive points to a local path",
                )
            findings.append(finding)
            continue

        if in_require_block:
            module_line = line.split("//", 1)[0].strip()
        elif line.startswith("require "):
            module_line = line[len("require ") :].split("//", 1)[0].strip()
        else:
            continue

        parts = module_line.split()
        if len(parts) >= 2:
            dependencies.append((line_number, parts[0], parts[1]))

    findings.extend(
        _scan_declared_dependencies(
            dependencies=dependencies,
            file_path=file_path,
            root=root,
        )
    )
    return findings


def _scan_pyproject(file_path: Path, root: Path) -> list[AuditFinding]:
    if tomllib is None:
        return []

    try:
        payload = tomllib.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return []

    dependencies: list[str] = []
    project = payload.get("project", {})
    dependencies.extend(project.get("dependencies", []))

    optional_groups = project.get("optional-dependencies", {})
    for group in optional_groups.values():
        dependencies.extend(group)

    return _scan_declared_dependencies(
        dependencies=dependencies,
        file_path=file_path,
        root=root,
    )


def _scan_requirements(file_path: Path, root: Path) -> list[AuditFinding]:
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    dependencies = [
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return _scan_declared_dependencies(
        dependencies=dependencies,
        file_path=file_path,
        root=root,
    )


def _scan_declared_dependencies(
    dependencies: Iterable[str | tuple[int, str, str]], file_path: Path, root: Path
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    relative_file = str(file_path.relative_to(root))

    for inferred_line_number, dependency in enumerate(dependencies, start=1):
        line_number, name, specifier, display = _normalize_dependency_input(
            dependency, inferred_line_number
        )
        baseline = DEPENDENCY_BASELINES.get(name.lower())

        if not specifier:
            findings.append(
                AuditFinding(
                    category="unbounded_dependency",
                    file=relative_file,
                    line=line_number,
                    severity="medium",
                    match=display,
                    detail="Dependency has no explicit version constraint",
                )
            )
            continue

        is_pinned = specifier.startswith("==") or specifier.startswith("v")
        if baseline and is_pinned:
            pinned_version = specifier[2:].strip() if specifier.startswith("==") else specifier
            if _normalize_version(pinned_version) < _normalize_version(baseline):
                findings.append(
                    AuditFinding(
                        category="outdated_dependency",
                        file=relative_file,
                        line=line_number,
                        severity="medium",
                        match=display,
                        detail=f"Pinned version appears older than the {baseline}+ baseline",
                    )
                )

    return findings


def _normalize_dependency_input(
    dependency: str | tuple[int, str, str], inferred_line_number: int
) -> tuple[int, str, str, str]:
    if isinstance(dependency, tuple):
        line_number, name, specifier = dependency
        display = f"{name} {specifier}"
        return line_number, name, specifier, display

    name, specifier = _split_dependency_spec(dependency)
    return inferred_line_number, name, specifier, dependency


def _split_dependency_spec(dependency: str) -> tuple[str, str]:
    match = re.match(r"([A-Za-z0-9_.-]+)\s*([<>=!~].+)?", dependency)
    if not match:
        return dependency.strip(), ""
    name = match.group(1).strip()
    specifier = (match.group(2) or "").strip()
    return name, specifier


def _normalize_version(version: str) -> tuple[int, ...]:
    numbers = re.findall(r"\d+", version)
    return tuple(int(number) for number in numbers) if numbers else (0,)


def _should_ignore_secret_line(category: str, line: str) -> bool:
    if category != "secret_keyword":
        return False
    return any(pattern.search(line) for pattern in SAFE_SECRET_PATTERNS)


def _iter_candidate_files(root: Path) -> Iterable[Path]:
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        if ".git" in file_path.parts or "__pycache__" in file_path.parts:
            continue
        if file_path.suffix.lower() in TEXT_EXTENSIONS or not file_path.suffix:
            yield file_path
