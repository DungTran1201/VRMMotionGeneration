# Experiment Workspace Operating Contract (`exp/AGENTS.md`)

This operating contract applies to all engineering and research work conducted within the `exp/` directory.

---

## 1. Boundary & Product Isolation
- Work strictly within `exp/`.
- **Never** introduce direct code imports, runtime dependencies, shared configs, or symlinks between `exp/` and `frontend/`, `backend/`, or `infra/`.
- Product builds must remain 100% functional without the contents or environment of `exp/`.

## 2. Evidence-First Experimentation
- Every experiment must record: hypothesis, exact command line, environment manifest hash, random seeds, hardware specifications (CPU/GPU/VRAM), stdout/stderr logs, duration, and metrics.
- Do not fabricate missing metrics. Use `NOT MEASURED` or `BLOCKED` when measurements are unavailable.
- Never represent synthetic data smoke-training as genuine model training on benchmark datasets.
- Never use a deterministic fixture to claim that deep learning inference is working.

## 3. Storage & Weight Hygiene
- **Zero Binary Weights in Git**: Checkpoint files (`*.ckpt`, `*.pt`, `*.bin`, `*.safetensors`, `*.onnx`) must never be committed to Git.
- Raw training datasets must be kept out of version control and documented with clear provenance and licensing in `exp/datasets/README.md`.
- Large run artifacts (tensors, raw videos) belong in `exp/artifacts/` and must be gitignored.

## 4. Promotion Criteria
- An experiment may only be integrated into the product after:
  1. Formal write-up in `exp/reports/`.
  2. Accepted Architecture Decision Record (ADR) in `docs/05-architecture/`.
  3. Stable canonical schema in `models/api/` or `models/domain/`.
  4. Full unit and contract test coverage in `backend/tests/` or `frontend/tests/`.
  5. Security and license audit sign-off in `docs/13-governance/`.
