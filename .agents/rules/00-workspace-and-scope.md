# Rule 00: Workspace and Scope

1. **Active Product Boundary**: The only active product is the unified Web + Electron Desktop application foundation sharing code in `frontend/`.
2. **Purged Legacy Domains**: All humanoid motion generation, kinematic retargeting, ARDY, MotionStreamer, DiP, MotionBricks, PyTorch, CUDA, checkpoints, and datasets are strictly excluded. Never reintroduce them.
3. **Shell Scope**: The application shell provides core navigation, overview, settings, diagnostics, and graceful platform adaptation. Do not introduce speculative multi-tenant backends, cloud synchronization, or billing systems without explicit requirements.
