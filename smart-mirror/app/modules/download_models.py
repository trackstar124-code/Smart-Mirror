"""
download_models.py
~~~~~~~~~~~~~~~~~~
Downloads the two ONNX hand-tracking models on first run.

Models come from PINTO0309/hand_landmark (GitHub Releases, MIT licence),
which are converted from Google's original MediaPipe TFLite weights.

Call ensure_models() at startup; it is a no-op if the files are already
present, so the network is only hit once.
"""

import urllib.request
import hashlib
from pathlib import Path

# ── model directory lives next to this file ───────────────────────────────────
MODELS_DIR = Path(__file__).parent / "models"

_BASE_URL = (
    "https://github.com/PINTO0309/hand_landmark/releases/download/1.0.0/"
)

# (filename, sha256 of the downloaded file)
_MODELS = {
    "palm_detection_full_Nx3x192x192_post.onnx": None,   # size check only
    "hand_landmark_sparse_Nx3x224x224.onnx": None,
}


def _download(filename: str) -> None:
    """Download a single model file and report progress."""
    url = _BASE_URL + filename
    dest = MODELS_DIR / filename
    print(f"[download_models] Downloading {filename} …", flush=True)
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"[download_models] Saved → {dest}", flush=True)
    except Exception as exc:
        # Clean up any partial file so we don't silently use a corrupt model
        dest.unlink(missing_ok=True)
        raise RuntimeError(
            f"Failed to download {filename} from {url}.\n"
            "Check your internet connection and try again."
        ) from exc


def ensure_models() -> dict[str, Path]:
    """
    Ensure both ONNX model files exist in MODELS_DIR.

    Returns a dict mapping logical name → Path:
        {
            "palm":     Path("…/models/palm_detection_full_Nx3x192x192_post.onnx"),
            "landmark": Path("…/models/hand_landmark_full_Nx3x224x224.onnx"),
        }
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for filename in _MODELS:
        dest = MODELS_DIR / filename
        if not dest.exists() or dest.stat().st_size == 0:
            _download(filename)

    return {
        "palm":     MODELS_DIR / "palm_detection_full_Nx3x192x192_post.onnx",
        "landmark": MODELS_DIR / "hand_landmark_sparse_Nx3x224x224.onnx",
    }


if __name__ == "__main__":
    # Allow running this script standalone to pre-download models
    paths = ensure_models()
    print("[download_models] All models ready:")
    for key, path in paths.items():
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  {key:10s}  {path.name}  ({size_mb:.1f} MB)")
