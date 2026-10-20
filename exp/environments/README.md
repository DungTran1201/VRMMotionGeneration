# `exp/environments/` — Experiment Environment Manifests

## Purpose
Maintains reproducible virtual environment manifests, dependency locks, and CUDA/PyTorch runtime specifications for experiment execution.

## What Belongs Here
- Pinned `requirements.txt`, `pyproject.toml`, or `environment.yaml` files.
- Container definitions specific to deep learning training or inference benchmarks.
- Environment verification instructions.

## What Must NOT Belong Here
- Production backend or frontend environment manifests (these belong in `backend/` and `frontend/`).
- Active virtualenv binaries (`.venv/`).

## Source-of-Truth Relationship
- Ensures experimental runs are reproducible and isolated from product dependency trees.
