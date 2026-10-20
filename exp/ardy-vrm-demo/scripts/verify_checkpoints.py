#!/usr/bin/env python3
"""
verify_checkpoints.py — Verify integrity, structure, and loading of ARDY checkpoints.
Checks safetensors weight files, config.yaml, and skeleton definition.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
import yaml


def hash_file(path: Path, max_bytes: int = 10_000_000) -> str:
    """Compute sha256 hash of file prefix for fast integrity check."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        chunk = f.read(max_bytes)
        h.update(chunk)
    return h.hexdigest()


def verify_checkpoint(ckpt_dir: Path) -> dict:
    result = {
        "checkpoint_dir": str(ckpt_dir.resolve()),
        "exists": ckpt_dir.exists(),
        "files": {},
        "config": {},
        "safetensors_test": {},
        "status": "FAIL",
    }

    if not ckpt_dir.exists():
        result["error"] = f"Directory not found: {ckpt_dir}"
        return result

    required_files = ["config.yaml", "denoiser.safetensors", "tokenizer.safetensors"]
    all_present = True

    for name in required_files:
        p = ckpt_dir / name
        present = p.exists()
        if not present:
            all_present = False
            result["files"][name] = {"present": False}
        else:
            size = p.stat().st_size
            prefix_hash = hash_file(p)
            result["files"][name] = {
                "present": True,
                "size_bytes": size,
                "size_mb": round(size / (1024**2), 2),
                "prefix_sha256": prefix_hash,
            }

    if not all_present:
        result["error"] = "Missing required checkpoint files"
        return result

    # Read config.yaml
    try:
        with open(ckpt_dir / "config.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            result["config"] = {
                "skeleton": cfg.get("skeleton", {}).get("name") if isinstance(cfg.get("skeleton"), dict) else cfg.get("skeleton"),
                "fps": cfg.get("motion_rep", {}).get("fps") if isinstance(cfg.get("motion_rep"), dict) else cfg.get("fps"),
                "gen_horizon_len": cfg.get("model", {}).get("gen_horizon_len"),
            }
    except Exception as e:
        result["config_error"] = str(e)

    # Test loading safetensors headers
    try:
        from safetensors import safe_open
        for name in ["tokenizer.safetensors", "denoiser.safetensors"]:
            p = ckpt_dir / name
            with safe_open(p, framework="pt", device="cpu") as f:
                keys = f.keys()
                result["safetensors_test"][name] = {
                    "can_open": True,
                    "key_count": len(keys),
                    "sample_keys": keys[:3],
                }
        result["status"] = "PASS"
    except Exception as e:
        result["safetensors_test"]["error"] = str(e)
        result["status"] = "FAIL"

    return result


def main():
    repo_root = Path(__file__).resolve().parent.parent
    ckpt_dir = repo_root / "checkpoints" / "ARDY-Core-RP-20FPS-Horizon8"
    if len(sys.argv) > 1:
        ckpt_dir = Path(sys.argv[1])

    res = verify_checkpoint(ckpt_dir)
    print(json.dumps(res, indent=2))
    if res["status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
