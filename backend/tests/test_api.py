"""Integration tests for FastAPI endpoints."""

import json
from pathlib import Path
import pytest
from starlette.testclient import TestClient

from motionbricks_vrm.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "mode_a_fixture_ready" in data
    assert "mode_b_real_inference_ready" in data
    assert "checkpoint_details" in data


def test_api_motion_schema(client):
    res = client.get("/api/motion/schema")
    assert res.status_code == 200
    schema = res.json()
    assert schema.get("title") == "CanonicalHumanoidMotion"
    assert "properties" in schema


def test_api_motion_fixture(client):
    res = client.get("/api/motion/fixture")
    assert res.status_code == 200
    fixture = res.json()
    assert fixture["schema"] == "CanonicalHumanoidMotion/v1"
    assert len(fixture["frames"]) > 0


def test_api_motion_validate_success(client):
    fixture_path = Path(__file__).resolve().parent.parent.parent / "fixtures" / "sample_motion.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    res = client.post("/api/motion/validate", json={"motion": payload})
    assert res.status_code == 200
    body = res.json()
    assert body["valid"] is True
    assert body["schema_version"] == "CanonicalHumanoidMotion/v1"
    assert body["frame_count"] == 60


def test_api_motion_validate_failure(client):
    invalid_payload = {
        "schema": "CanonicalHumanoidMotion/v1",
        "metadata": {
            "source": "fixture",
            "fps": 30.0,
            "duration": 1.0,
            "num_frames": 1,
        },
        "frames": [
            {
                "timestamp": 0.0,
                "root": {"position": [0.0, 0.0, 0.0], "rotation": [0.0, 0.0, 0.0, 1.0]},
                "bones": {
                    "hips": {"rotation": [999.0, 0.0, 0.0, 0.0]}  # non-unit quaternion!
                }
            }
        ]
    }
    res = client.post("/api/motion/validate", json={"motion": invalid_payload})
    assert res.status_code == 200
    body = res.json()
    assert body["valid"] is False
    assert len(body["errors"]) > 0


def test_api_inference_generate_unavailable(client):
    # When checkpoints are LFS pointers or missing, returns 503 with explicit instructions
    res = client.post("/api/inference/generate", json={"command": "walk", "duration_seconds": 2.0})
    # Since checkpoints in the test workspace are LFS pointers, it must return 503
    assert res.status_code == 503
    detail = res.json()["detail"]
    assert "Real MotionBricks inference unavailable" in detail["error"]
    assert "git lfs pull" in detail["suggested_action"]
