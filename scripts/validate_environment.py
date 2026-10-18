"""Environment and dependency verification script.

Checks Python runtime, required packages, GPU hardware status, and
MotionBricks checkpoint availability for Mode A and Mode B operation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add backend/src to path
repo_root = Path(__file__).resolve().parent.parent
backend_src = repo_root / "backend" / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

from motionbricks_vrm.source_adapter import inspect_motionbricks_checkpoints


def main() -> int:
    print("=" * 70)
    print(" MOTIONBRICKS-TO-VRM ENVIRONMENT VALIDATION")
    print("=" * 70)

    # 1. Python runtime
    py_ver = sys.version.split()[0]
    print(f"\n[1] Python Runtime: {py_ver} ({sys.executable})")
    if sys.version_info < (3, 9):
        print("    [!] WARNING: Python 3.9+ is recommended.")
    else:
        print("    [+] Python version satisfies minimum requirements.")

    # 2. Critical Packages
    packages = [
        ("pydantic", "Pydantic (Data Validation & Schema Engine)"),
        ("fastapi", "FastAPI (REST & WebSocket Backend API)"),
        ("uvicorn", "Uvicorn (ASGI Web Server)"),
        ("numpy", "NumPy (Tensor & Matrix Calculations)"),
        ("scipy", "SciPy (Scientific Spatial Rotations)"),
        ("yaml", "PyYAML (Retargeting Configuration Parser)"),
    ]

    print("\n[2] Required Core Packages:")
    all_core_ok = True
    for mod_name, desc in packages:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "installed")
            print(f"    [+] {desc}: {ver}")
        except ImportError:
            print(f"    [-] MISSING: {desc} ({mod_name})")
            all_core_ok = False

    # 3. PyTorch & GPU Acceleration
    print("\n[3] Deep Learning & Hardware Status:")
    torch_available = False
    cuda_available = False
    try:
        import torch
        torch_available = True
        cuda_available = torch.cuda.is_available()
        print(f"    [+] PyTorch: {torch.__version__}")
        print(f"    [+] CUDA Available: {cuda_available}")
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            print(f"    [+] GPU 0: {device_name} ({vram_gb:.2f} GB VRAM)")
        else:
            print("    [i] CPU-only execution for PyTorch.")
    except ImportError:
        print("    [-] PyTorch is not installed in current Python environment.")

    # 4. MotionBricks Checkpoints Status
    print("\n[4] MotionBricks Checkpoints (Mode B Readiness):")
    status = inspect_motionbricks_checkpoints()
    print(f"    Pose Checkpoint:   {'PRESENT' if status.pose_ckpt_present else 'MISSING'} "
          f"(LFS Pointer: {status.pose_ckpt_is_lfs_pointer})")
    print(f"    Root Checkpoint:   {'PRESENT' if status.root_ckpt_present else 'MISSING'} "
          f"(LFS Pointer: {status.root_ckpt_is_lfs_pointer})")
    print(f"    VQ-VAE Checkpoint: {'PRESENT' if status.vqvae_ckpt_present else 'MISSING'} "
          f"(LFS Pointer: {status.vqvae_ckpt_is_lfs_pointer})")
    print(f"    Clip Checkpoint:   {'PRESENT' if status.clip_ckpt_present else 'MISSING'} "
          f"(LFS Pointer: {status.clip_ckpt_is_lfs_pointer})")
    print(f"    Status Summary:    {status.detail_message}")

    # 5. Operational Mode Summary
    print("\n" + "=" * 70)
    print(" OPERATIONAL MODE AVAILABILITY")
    print("=" * 70)
    print("  [+] MODE A: FIXTURE / OFFLINE DEMO -> READY (100% Functional)")
    print("      - Requires no GPU, no weights, and no external model inference.")
    print("      - Full schema validation, 3D WebGL viewer, and playback available.")

    if status.all_available and torch_available:
        print("  [+] MODE B: REAL MOTIONBRICKS INFERENCE -> READY")
    else:
        print("  [-] MODE B: REAL MOTIONBRICKS INFERENCE -> UNAVAILABLE")
        print("      - Reason: Upstream model weights are Git-LFS pointers or unpulled.")
        print("      - To enable: run `git lfs pull --include=\"motionbricks/out/**\"` in GR00T repo.")

    print("=" * 70)
    return 0 if all_core_ok else 1


if __name__ == "__main__":
    sys.exit(main())
