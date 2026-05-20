"""Build a minimal arXiv source zip from the prepared paper directory."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

INPUT_DIR = Path("paper/arxiv")
OUTPUT_DIR = Path("arxiv_submission")
ZIP_PATH = Path("submission_v1.zip")

INCLUDE_FILES = (
    "audit_probes_technical_report.tex",
    "figures/data_flow_cover_v010.png",
    "figures/telemetry_baseline_v010.png",
)

def copy_source_package() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    for relative_name in INCLUDE_FILES:
        source = INPUT_DIR / relative_name
        if not source.exists():
            raise FileNotFoundError(f"Missing required arXiv source file: {source}")
        if source.stat().st_size == 0:
            raise ValueError(f"Refusing to package empty arXiv source file: {source}")

        destination = OUTPUT_DIR / relative_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

def zip_source_package() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUTPUT_DIR.rglob("*")):
            if path.is_file():
                arcname = path.relative_to(OUTPUT_DIR).as_posix()
                archive.write(path, arcname)

def main() -> None:
    copy_source_package()
    zip_source_package()
    print(f"Ready for arXiv source upload: {ZIP_PATH}")

if __name__ == "__main__":
    main()
