#!/usr/bin/env python3
"""
check_environment.py — Non-mutating environment inspection for DiP + Viser.
Verifies Python version, PyTorch, CUDA, RAM, disk space, and essential packages.
Does NOT download large files or alter global state.
"""

import sys
import os
import platform
import shutil
import psutil

def check_env() -> dict:
    results = {
        "os": platform.platform(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "is_64bit": sys.maxsize > 2**32,
        "torch_available": False,
        "torch_version": None,
        "cuda_available": False,
        "cuda_device_name": None,
        "cuda_vram_gb": None,
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "packages": {}
    }

    # Check torch
    try:
        import torch
        results["torch_available"] = True
        results["torch_version"] = torch.__version__
        results["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            results["cuda_device_name"] = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            results["cuda_vram_gb"] = round(props.total_memory / (1024**3), 2)
    except ImportError:
        pass

    # Check dependencies
    dependencies = [
        "transformers",
        "viser",
        "numpy",
        "scipy",
        "tqdm"
    ]
    for pkg in dependencies:
        try:
            mod = __import__(pkg)
            results["packages"][pkg] = getattr(mod, "__version__", "installed")
        except ImportError:
            results["packages"][pkg] = "MISSING"

    # Disk space for current directory
    total, used, free = shutil.disk_usage(".")
    results["disk_free_gb"] = round(free / (1024**3), 2)

    return results

def print_report(res: dict) -> int:
    print("=" * 60)
    print("DiP + Viser Environment Audit Report")
    print("=" * 60)
    print(f"OS Platform        : {res['os']}")
    print(f"Python Executable  : {res['python_executable']}")
    print(f"Python Version     : {res['python_version']} (64-bit: {res['is_64bit']})")
    print(f"System RAM         : {res['ram_available_gb']} GB available / {res['ram_total_gb']} GB total")
    print(f"Disk Free Space    : {res['disk_free_gb']} GB free on current drive")
    
    print("-" * 60)
    if res["torch_available"]:
        print(f"PyTorch Version    : {res['torch_version']}")
        print(f"CUDA Available     : {res['cuda_available']}")
        if res["cuda_available"]:
            print(f"CUDA Device        : {res['cuda_device_name']} ({res['cuda_vram_gb']} GB VRAM)")
        else:
            print("CUDA Device        : None (CPU fallback mode)")
    else:
        print("PyTorch Version    : NOT INSTALLED")

    print("-" * 60)
    print("Package Status:")
    for pkg, ver in res["packages"].items():
        status = "OK" if ver != "MISSING" else "MISSING"
        print(f"  - {pkg:<16}: {ver:<16} [{status}]")
    print("=" * 60)

    # Criteria for readiness
    if not res["torch_available"]:
        print("[FAIL] PyTorch is required for DiP execution.")
        return 1
    
    missing_critical = [p for p, v in res["packages"].items() if v == "MISSING" and p in ("transformers", "viser", "numpy")]
    if missing_critical:
        print(f"[WARN] Critical packages missing: {', '.join(missing_critical)}")
        return 2

    print("[PASS] Minimal environment requirements verified.")
    return 0

if __name__ == "__main__":
    results = check_env()
    code = print_report(results)
    sys.exit(code)
