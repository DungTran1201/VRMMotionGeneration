"""Motion document validation script.

Validates any JSON file against CanonicalHumanoidMotion/v1 specification,
verifying quaternion norms, timestamp monotonicity, schema fields, and bounds.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add backend/src to path
repo_root = Path(__file__).resolve().parent.parent
backend_src = repo_root / "backend" / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

from pydantic import ValidationError
from motionbricks_vrm.schemas.canonical_motion import CanonicalHumanoidMotion


def validate_file(file_path: Path) -> bool:
    print(f"Validating motion file: {file_path}")
    if not file_path.exists():
        print(f"[-] ERROR: File does not exist: {file_path}")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[-] ERROR: Failed to parse JSON: {e}")
        return False

    try:
        motion = CanonicalHumanoidMotion.model_validate(data)
        meta = motion.metadata
        print("[+] Schema Validation SUCCESSFUL!")
        print(f"    - Schema:            {motion.schema_}")
        print(f"    - Source:            {meta.source.value}")
        print(f"    - FPS:               {meta.fps}")
        print(f"    - Duration:          {meta.duration:.4f}s")
        print(f"    - Frame Count:       {meta.num_frames}")
        print(f"    - Coordinate System: {meta.coordinate_system.value}")
        print(f"    - Rotation Format:   {meta.rotation_format.value}")
        print(f"    - Profile:           {meta.retargeting_profile or 'default'}")

        # Check bone coverage
        first_frame = motion.frames[0]
        num_bones = len(first_frame.bones)
        print(f"    - Active Bones:      {num_bones} joints per frame")
        return True
    except ValidationError as ve:
        print("[-] Schema Validation FAILED with errors:")
        for err in ve.errors():
            loc = " -> ".join(str(p) for p in err["loc"])
            print(f"    * [{loc}] {err['msg']}")
        return False
    except Exception as e:
        print(f"[-] Validation FAILED with unexpected exception: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CanonicalHumanoidMotion/v1 documents")
    parser.add_argument(
        "file",
        nargs="?",
        default=str(repo_root / "fixtures" / "sample_motion.json"),
        help="Path to JSON motion file"
    )
    args = parser.parse_args()

    success = validate_file(Path(args.file))
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
