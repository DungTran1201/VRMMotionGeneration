"""Integration tests for frontend markup, truthful telemetry, and UI contract."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from ardy_vrm_demo.api import app

client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[4]  # exp/ardy-vrm-demo
INDEX_HTML = REPO_ROOT / "frontend" / "index.html"
INDEX_CSS = REPO_ROOT / "frontend" / "src" / "styles" / "index.css"


def test_no_hardcoded_fake_telemetry_in_markup():
    """Ensure hardcoded example metric values (1,625 ms, 36.9 FPS, etc.) are eliminated."""
    assert INDEX_HTML.exists()
    content = INDEX_HTML.read_text(encoding="utf-8")

    # Prohibited prefilled fake values
    forbidden_fakes = [
        "1,625 ms",
        "36.9 FPS",
        "0.54 (<1.0x Realtime)",
        "1,635 ms",
        "885.4 MB",
    ]

    for fake_val in forbidden_fakes:
        assert fake_val not in content, f"Forbidden hardcoded fake telemetry found in index.html: {fake_val}"


def test_truthful_metric_placeholders():
    """Ensure metric fields are initialized with truthful '—' or 'Idle' placeholders."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    assert 'id="metricStatus" class="metric-value">Idle</span>' in content
    assert 'id="metricDuration" class="metric-value">—</span>' in content
    assert 'id="metricGenTime" class="metric-value">—</span>' in content
    assert 'id="metricEffectiveFps" class="metric-value">—</span>' in content
    assert 'id="metricRtf" class="metric-value">—</span>' in content
    assert 'id="metricLatency" class="metric-value">—</span>' in content
    assert 'id="metricVram" class="metric-value">N/A</span>' in content
    assert 'id="metricRenderFps" class="metric-value">—</span>' in content


def test_authoritative_single_file_input():
    """Ensure there is exactly one file input and no duplicate nested event hack."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    assert '<input type="file" id="vrmFileInput" accept=".vrm"' in content
    assert "document.getElementById('vrmFileInput').files = this.files" not in content


def test_single_stage_canvas_and_floating_windows():
    """Ensure architecture uses a single stage canvas and customizable floating windows."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    assert '<canvas id="stageCanvas"' in content
    assert 'id="winMotionControls" class="floating-window"' in content
    assert 'id="winTelemetry" class="floating-window"' in content
    assert 'class="floating-timeline-bar"' in content

    # Old dual viewports must no longer be present
    assert '<canvas id="skeletonCanvas"' not in content
    assert '<canvas id="vrmCanvas"' not in content


def test_pinned_import_map_with_external_three():
    """Ensure @pixiv/three-vrm specifies external=three to avoid multiple Three.js instances."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    assert '"three": "https://esm.sh/three@0.170.0"' in content
    assert '"@pixiv/three-vrm": "https://esm.sh/@pixiv/three-vrm@3.3.4?external=three"' in content


def test_fullscreen_css_rules():
    """Verify CSS implements 100dvw/100dvh full-page stage without main container scrollbars."""
    assert INDEX_CSS.exists()
    css = INDEX_CSS.read_text(encoding="utf-8")
    assert "100dvw" in css
    assert "100dvh" in css
    assert ".floating-window" in css
    assert ".floating-timeline-bar" in css
