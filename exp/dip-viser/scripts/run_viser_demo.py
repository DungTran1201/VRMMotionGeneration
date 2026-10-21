"""
Entrypoint script for DiP-Viser Interactive Demo.
Starts the browser-based 3D skeleton motion viewer.
"""
import argparse
import sys
import time
from pathlib import Path

# Add experiment root to sys.path
EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from app.config import DEFAULT_HOST, DEFAULT_PORT
from app.viewer import ViserMotionViewer


def main():
    parser = argparse.ArgumentParser(description="Launch DiP Text-to-Motion Viser Viewer")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Host address to bind server (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on (default: 8080)")
    args = parser.parse_args()

    print("=" * 60)
    print(" DiP (Diffusion Planner) Text-to-Motion 3D Viewer")
    print("=" * 60)
    print(f"Starting Viser server on http://{args.host}:{args.port}")
    print("Opening this URL in your web browser allows full 3D interactive viewing.")
    print("Press Ctrl+C to exit.\n")

    viewer = ViserMotionViewer(host=args.host, port=args.port)

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping Viser server...")
        viewer.stop()
        print("Viewer stopped cleanly.")


if __name__ == "__main__":
    main()
