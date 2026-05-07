import os
import subprocess
import shutil
import re

# --- CONFIGURATION ---
INPUT_DIR = "paper/arxiv"
OUTPUT_DIR = "arxiv_submission"
ZIP_NAME = "submission_v1.zip"


def check_unescaped_percent(directory):
    """Scans .tex files for '%' signs not preceded by '\'."""
    pattern = re.compile(r'(?<!\\)%')
    issues_found = False
    
    print("Checking for unescaped '%' in math/text...")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".tex"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        # Ignore lines that are clearly just comments
                        if line.strip().startswith('%'):
                            continue
                        if pattern.search(line):
                            print(f"Potential issue in {file} (Line {i}): {line.strip()}")
                            issues_found = True
    return issues_found


def main():
    # 1. Run Safety Check
    # Check the INPUT_DIR first to fix them before distilling
    warning = check_unescaped_percent(INPUT_DIR)
    if warning:
        proceed = input("Unescaped '%' found. They might break your math. Proceed anyway? (y/n): ")
        if proceed.lower() != 'y':
            return

    # 2. Clean the LaTeX
    print(f"Distilling {INPUT_DIR}...")
    subprocess.run(["arxiv_latex_cleaner", INPUT_DIR, "--output_full_path", OUTPUT_DIR])

    # 3. Zip it for ArXiv
    print(f"Zipping for ArXiv: {ZIP_NAME}...")
    shutil.make_archive(ZIP_NAME.replace(".zip", ""), 'zip', OUTPUT_DIR)

    print(f"Ready! Upload {ZIP_NAME} to arXiv.")


if __name__ == "__main__":
    main()
