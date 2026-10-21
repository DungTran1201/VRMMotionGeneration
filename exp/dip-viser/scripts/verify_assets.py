#!/usr/bin/env python3
"""
verify_assets.py — Non-mutating asset verification for DiP + Viser.
Verifies the existence, size, and validity of checkpoints, configs, and datasets.
Does NOT download large files or mutate the workspace.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

EXPECTED_CHECKPOINTS = [
    {
        "alias": "DiP_no-target_model000600343",
        "relative_path": "checkpoints/DiP_no-target_10steps_context20_predict40/model000600343.pt",
        "expected_min_bytes": 200_000_000,
        "type": "model_weights"
    },
    {
        "alias": "DiP_args_config",
        "relative_path": "checkpoints/DiP_no-target_10steps_context20_predict40/args.json",
        "expected_min_bytes": 100,
        "type": "json_config"
    }
]

EXPECTED_DATASET_ASSETS = [
    {
        "alias": "HumanML3D_Mean",
        "relative_path": "upstream/motion-diffusion-model/dataset/t2m_mean.npy",
        "fallback_path": "dataset/HumanML3D/Mean.npy",
        "type": "normalization_stats"
    },
    {
        "alias": "HumanML3D_Std",
        "relative_path": "upstream/motion-diffusion-model/dataset/t2m_std.npy",
        "fallback_path": "dataset/HumanML3D/Std.npy",
        "type": "normalization_stats"
    }
]

def check_file(exp_root: Path, item: dict) -> dict:
    target_path = exp_root / item["relative_path"]
    found = target_path.exists()
    fallback_used = False
    
    if not found and "fallback_path" in item:
        fallback = exp_root / item["fallback_path"]
        if fallback.exists():
            target_path = fallback
            found = True
            fallback_used = True

    info = {
        "alias": item["alias"],
        "path": str(target_path),
        "found": found,
        "size_bytes": 0,
        "valid": False,
        "notes": ""
    }

    if found:
        size = target_path.stat().st_size
        info["size_bytes"] = size
        min_bytes = item.get("expected_min_bytes", 1)
        if size < min_bytes:
            info["notes"] = f"File exists but is suspiciously small ({size} bytes < {min_bytes} min bytes, possibly LFS pointer or HTML error page)"
            info["valid"] = False
        else:
            # Check JSON if config
            if item.get("type") == "json_config":
                try:
                    with open(target_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    info["notes"] = f"Valid JSON, {len(data)} parameters."
                    info["valid"] = True
                except Exception as e:
                    info["notes"] = f"Corrupt JSON: {e}"
                    info["valid"] = False
            else:
                info["valid"] = True
                if fallback_used:
                    info["notes"] = "Located via fallback path."
                else:
                    info["notes"] = "Verified on disk."
    else:
        info["notes"] = "Asset not found on disk."

    return info

def verify_all(exp_root: Path = None) -> tuple[list, bool]:
    if exp_root is None:
        # Default to exp/dip-viser directory
        script_dir = Path(__file__).resolve().parent
        exp_root = script_dir.parent

    results = []
    all_ok = True

    for item in EXPECTED_CHECKPOINTS:
        res = check_file(exp_root, item)
        results.append(res)
        if not res["valid"]:
            all_ok = False

    for item in EXPECTED_DATASET_ASSETS:
        res = check_file(exp_root, item)
        results.append(res)
        if not res["valid"]:
            all_ok = False

    return results, all_ok

def print_report(results: list, all_ok: bool) -> int:
    print("=" * 70)
    print("DiP Asset & Checkpoint Verification Report")
    print("=" * 70)
    for res in results:
        status_str = "READY" if res["valid"] else "MISSING / INVALID"
        print(f"[{status_str:<17}] {res['alias']}")
        print(f"  Path : {res['path']}")
        print(f"  Size : {res['size_bytes']:,} bytes")
        print(f"  Notes: {res['notes']}")
        print()
    print("=" * 70)
    if all_ok:
        print("[PASS] All required checkpoints and assets are verified on disk.")
        return 0
    else:
        print("[BLOCKED] One or more required assets are missing or unverified.")
        return 1

if __name__ == "__main__":
    results, ok = verify_all()
    code = print_report(results, ok)
    sys.exit(code)
