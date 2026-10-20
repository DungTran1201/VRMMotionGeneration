#!/usr/bin/env python3
"""
validate_layout.py — Deterministic directory and layout validation for VRMMotionGeneration.
Ensures that the clean Operation Dev workspace scaffold conforms to the required layout,
contains the required README placeholders, preserves boundary isolation, and avoids
accidental source/build remnants.
"""

import sys
import os
from pathlib import Path

REQUIRED_FILES = [
    ".gitignore",
    "AGENTS.md",
    "README.md",
    ".agents/README.md",
    "frontend/README.md",
    "frontend/apps/web/README.md",
    "frontend/public/README.md",
    "frontend/tests/README.md",
    "backend/README.md",
    "backend/src/README.md",
    "backend/migrations/README.md",
    "backend/tests/README.md",
    "infra/README.md",
    "infra/scripts/README.md",
    "infra/ci/README.md",
    "infra/deployment/README.md",
    "infra/observability/README.md",
    "docs/README.md",
    "docs/00-discovery/README.md",
    "docs/01-planning/README.md",
    "docs/02-requirements/README.md",
    "docs/03-business-process/README.md",
    "docs/04-use-cases/README.md",
    "docs/05-architecture/README.md",
    "docs/06-domain/README.md",
    "docs/07-api/README.md",
    "docs/08-behavior/README.md",
    "docs/09-security/README.md",
    "docs/10-ux/README.md",
    "docs/11-testing/README.md",
    "docs/12-operations/README.md",
    "docs/13-governance/README.md",
    "diagrams/README.md",
    "diagrams/context/README.md",
    "diagrams/architecture/README.md",
    "diagrams/processes/README.md",
    "diagrams/sequence/README.md",
    "diagrams/state/README.md",
    "diagrams/data-flow/README.md",
    "diagrams/deployment/README.md",
    "diagrams/ux/README.md",
    "models/README.md",
    "models/context/README.md",
    "models/requirements/README.md",
    "models/process/README.md",
    "models/architecture/README.md",
    "models/domain/README.md",
    "models/api/README.md",
    "models/interaction/README.md",
    "models/security/README.md",
    "models/ux/README.md",
    "models/testing/README.md",
    "models/deployment/README.md",
    "exp/README.md",
    "exp/AGENTS.md",
    "exp/.gitignore",
    "exp/experiments/README.md",
    "exp/scripts/README.md",
    "exp/environments/README.md",
    "exp/datasets/README.md",
    "exp/checkpoints/README.md",
    "exp/artifacts/README.md",
    "exp/reports/README.md",
]

def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    print(f"[validate_layout] Validating repository root: {repo_root}")

    errors = []
    
    # Check required paths
    for rel_path in REQUIRED_FILES:
        target = repo_root / rel_path
        if not target.exists():
            errors.append(f"MISSING: {rel_path}")
        elif target.is_file() and target.stat().st_size == 0:
            errors.append(f"EMPTY FILE: {rel_path} (must contain usage/purpose guidance)")

    # Check for symlinks in exp/ pointing outside exp/
    exp_dir = repo_root / "exp"
    if exp_dir.exists():
        for root, dirs, files in os.walk(exp_dir):
            for name in dirs + files:
                p = Path(root) / name
                if p.is_symlink():
                    resolved = p.resolve()
                    if not str(resolved).startswith(str(exp_dir.resolve())):
                        errors.append(f"PROHIBITED SYMLINK: {p} points outside exp/: {resolved}")

    # Verify no accidental checkpoints or large binaries committed in scaffold
    forbidden_extensions = {".ckpt", ".pt", ".pth", ".safetensors", ".onnx", ".bin"}
    for root, dirs, files in os.walk(repo_root):
        # Ignore .git directory
        if ".git" in Path(root).parts:
            continue
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in forbidden_extensions:
                errors.append(f"PROHIBITED CHECKPOINT/WEIGHT FILE FOUND: {Path(root) / file}")

    if errors:
        print(f"[validate_layout] FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"[validate_layout] PASSED: All {len(REQUIRED_FILES)} required scaffold paths verified.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
