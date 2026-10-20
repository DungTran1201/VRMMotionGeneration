#!/usr/bin/env python3
"""
check_environment.py — Environment and hardware probe for ARDY VRM Demo.
Probes CPU, RAM, GPU, CUDA, drivers, disk space, Python/Node tools,
and Hugging Face access without exposing secrets.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def probe_system() -> dict:
    probe = {
        "os": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "hardware": {},
        "gpu": {},
        "runtimes": {},
        "ardy": {},
        "huggingface": {},
    }

    # Disk space
    try:
        usage = shutil.disk_usage(".")
        probe["hardware"]["disk_free_gb"] = round(usage.free / (1024**3), 2)
        probe["hardware"]["disk_total_gb"] = round(usage.total / (1024**3), 2)
    except Exception as e:
        probe["hardware"]["disk_error"] = str(e)

    # CPU info
    probe["hardware"]["cpu_count"] = os.cpu_count()

    # GPU probe via nvidia-smi
    nvidia_smi = shutil.which("nvidia-smi")
    probe["gpu"]["nvidia_smi_available"] = nvidia_smi is not None
    if nvidia_smi:
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free", "--format=csv,noheader,nounits"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            parts = [p.strip() for p in out.split(",")]
            if len(parts) >= 4:
                probe["gpu"]["name"] = parts[0]
                probe["gpu"]["driver_version"] = parts[1]
                probe["gpu"]["vram_total_mb"] = float(parts[2])
                probe["gpu"]["vram_free_mb"] = float(parts[3])
        except Exception as e:
            probe["gpu"]["nvidia_smi_error"] = str(e)

    # PyTorch and CUDA check
    try:
        import torch
        probe["gpu"]["torch_version"] = torch.__version__
        probe["gpu"]["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            probe["gpu"]["device_name"] = torch.cuda.get_device_name(0)
            probe["gpu"]["cuda_version"] = torch.version.cuda
    except ImportError:
        probe["gpu"]["torch_version"] = "NOT_INSTALLED"
        probe["gpu"]["cuda_available"] = False

    # Node & npm
    for cmd in ["node", "npm", "uv", "git"]:
        path = shutil.which(cmd)
        probe["runtimes"][cmd] = path is not None
        if path:
            try:
                ver = subprocess.check_output([cmd, "--version"], text=True, stderr=subprocess.DEVNULL).strip()
                probe["runtimes"][f"{cmd}_version"] = ver
            except Exception:
                pass

    # Hugging Face token probe (safe, no secret exposure)
    token_file = Path.home() / ".cache" / "huggingface" / "token"
    has_token_env = "HF_TOKEN" in os.environ or "HUGGING_FACE_HUB_TOKEN" in os.environ
    has_token_file = token_file.exists() and token_file.stat().st_size > 0
    probe["huggingface"]["token_available"] = has_token_env or has_token_file
    probe["huggingface"]["gated_access_status"] = (
        "TOKEN_PRESENT" if (has_token_env or has_token_file) else "BLOCKED_GATED_MODEL_ACCESS"
    )

    # ARDY vendor and checkpoint check
    repo_root = Path(__file__).resolve().parent.parent
    vendor_ardy = repo_root / "vendor" / "ardy"
    probe["ardy"]["vendor_dir_exists"] = vendor_ardy.exists()
    if vendor_ardy.exists():
        try:
            head = subprocess.check_output(
                ["git", "-C", str(vendor_ardy), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            probe["ardy"]["vendor_git_commit"] = head
        except Exception:
            probe["ardy"]["vendor_git_commit"] = "UNKNOWN"

    ckpt_dir = repo_root / "checkpoints" / "ARDY-Core-RP-20FPS-Horizon8"
    probe["ardy"]["checkpoint_dir_exists"] = ckpt_dir.exists()
    if ckpt_dir.exists():
        denoiser = ckpt_dir / "denoiser.safetensors"
        tokenizer = ckpt_dir / "tokenizer.safetensors"
        config_yaml = ckpt_dir / "config.yaml"
        probe["ardy"]["denoiser_present"] = denoiser.exists() and denoiser.stat().st_size > 100_000_000
        probe["ardy"]["tokenizer_present"] = tokenizer.exists() and tokenizer.stat().st_size > 10_000_000
        probe["ardy"]["config_present"] = config_yaml.exists()
        probe["ardy"]["checkpoint_ready"] = (
            probe["ardy"]["denoiser_present"] and probe["ardy"]["tokenizer_present"] and probe["ardy"]["config_present"]
        )

    return probe


def main():
    probe = probe_system()
    print(json.dumps(probe, indent=2))


if __name__ == "__main__":
    main()
