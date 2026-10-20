# `exp/scripts/` — Experiment Execution Scripts

## Purpose
Maintains standalone scripts for training, fine-tuning, benchmark evaluation, and offline data conversion.

## What Belongs Here
- Model execution scripts for running inference benchmarks.
- Dataset preprocessing and normalization scripts.
- Metric calculation utilities (e.g. MPJPE, FID, foot sliding measurements).

## What Must NOT Belong Here
- Scripts called directly by production services in `backend/` or `frontend/`.
- Hardcoded user paths or unparameterized commands.

## Source-of-Truth Relationship
- Scripts operate within the environments defined in `exp/environments/`.
