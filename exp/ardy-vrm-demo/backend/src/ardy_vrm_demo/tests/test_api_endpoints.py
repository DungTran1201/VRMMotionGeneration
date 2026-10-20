"""Integration/Unit tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from ardy_vrm_demo.api import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns valid system status and GPU/checkpoint info."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mode"] in ("LIVE ARDY", "FIXTURE PREVIEW")
    assert data["torch_version"] is not None
    assert "checkpoint_ready" in data


def test_models_endpoint():
    """Verify models endpoint returns supported models and checkpoint availability."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    models = {m["alias"]: m for m in data["models"]}
    assert "core8" in models
    assert models["core8"]["skeleton"] == "CoreSkeleton27"
    assert models["core8"]["fps"] == 20.0


def test_default_sample_endpoint():
    """Verify default motion sample can be fetched and conforms to schema."""
    response = client.get("/api/samples/default")
    assert response.status_code == 200
    data = response.json()
    assert "total_frames" in data
    assert data["total_frames"] > 0
    assert "fps" in data
    assert "vrm" in data
    assert "skeleton" in data
    assert "bones" in data["vrm"]
    assert "hips" in data["vrm"]["bones"]
    assert "telemetry" in data


def test_generation_request_validation():
    """Verify request validation rejects invalid duration and empty prompts."""
    # Empty prompt
    resp_empty = client.post(
        "/api/generations",
        json={"prompt": "   ", "duration_seconds": 3.0},
    )
    assert resp_empty.status_code == 422

    # Duration below minimum (< 0.5s)
    resp_low = client.post(
        "/api/generations",
        json={"prompt": "A person walks", "duration_seconds": 0.2},
    )
    assert resp_low.status_code == 422

    # Duration above maximum (> 10.0s)
    resp_high = client.post(
        "/api/generations",
        json={"prompt": "A person walks", "duration_seconds": 25.0},
    )
    assert resp_high.status_code == 422


def test_nonexistent_job_returns_404():
    """Requesting status of non-existent job must return 404."""
    response = client.get("/api/generations/job-non-existent-999")
    assert response.status_code == 404


def test_cancel_nonexistent_job():
    """Cancelling a non-existent job must return 400."""
    response = client.post("/api/generations/job-non-existent-999/cancel")
    assert response.status_code == 400


def test_index_and_static_serving():
    """Verify root index.html and static assets are served properly."""
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "ARDY → VRM Motion Lab" in res_index.text

    res_css = client.get("/static/src/styles/index.css")
    assert res_css.status_code == 200
    assert "Design System" in res_css.text
