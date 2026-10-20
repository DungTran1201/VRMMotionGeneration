# `exp/` — Standalone Experiment Workspace

> **Critical Notice: Experiment Isolation Boundary**  
> The `exp/` workspace is a standalone, isolated engineering environment for machine learning experiments, model fine-tuning, motion generation benchmarks, and exploratory spikes.  
> **It is NOT part of the website application product.**

## Non-Negotiable Isolation Rules
1. **No Direct Imports**: Product code in `frontend/`, `backend/`, or `infra/` must **never** import modules or scripts from `exp/`.
2. **No Symlinks or Submodules**: Do not symlink files or directories between `exp/` and production directories.
3. **No Shared Runtime Packages**: Do not create a shared package specifically to connect `exp/` to the web application.
4. **Independent Lifecycle**: `exp/` maintains its own `AGENTS.md`, `.gitignore`, environments, execution scripts, and reporting structures.
5. **Promotion Gate**: Successful experiment outcomes may only be promoted into production via a dedicated work item, formal ADR (`docs/05-architecture/`), security review, canonical contract (`models/api/`), and automated test suite.

## Directory Structure
- `experiments/`: Experiment logs, hypothesis records, and exploratory notebooks.
- `scripts/`: Standalone experiment execution, data preprocessing, and evaluation scripts.
- `environments/`: Python virtual environment manifests (e.g. `requirements.txt`, conda `environment.yaml`).
- `datasets/`: Dataset storage policy and documentation (no raw datasets committed).
- `checkpoints/`: Model weight checkpoint policy and documentation (no weights committed).
- `artifacts/`: Generated tensors, logs, and evaluation metrics (gitignored).
- `reports/`: Markdown experiment summaries, benchmark findings, and promotion recommendations.
