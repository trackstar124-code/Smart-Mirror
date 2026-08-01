"""
gestures.py
~~~~~~~~~~~
Hand gesture recognition using OpenCV + ONNX Runtime.

This module replaces the MediaPipe dependency with a two-stage ONNX pipeline:
    Stage 1 – Palm Detector  : locates the hand bounding box in the full frame.
    Stage 2 – Hand Landmark  : regresses 21 3-D keypoints from the cropped hand.

The keypoint data is wrapped in a Landmark / HandResult dataclass that is
API-compatible with MediaPipe's NormalizedLandmark, so detect_gesture() and
the swipe logic are unchanged from the original implementation.
"""

import cv2
import numpy as np
import onnxruntime as ort
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os

import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent))   # ensure modules/ dir is importable
from download_models import ensure_models

# ── Shared state file ──────────────────────────────────────────────────────────
STATE_FILE = Path(__file__).parent / "gesture_state.txt"

# ── MediaPipe-compatible hand connection topology (21 landmarks) ───────────────
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),           # index
    (0, 9), (9, 10), (10, 11), (11, 12),      # middle
    (0, 13), (13, 14), (14, 15), (15, 16),    # ring
    (0, 17), (17, 18), (18, 19), (19, 20),    # pinky
    (5, 9), (9, 13), (13, 17),                # palm knuckles
]

# ── Inference constants ────────────────────────────────────────────────────────
PALM_INPUT_SIZE  = 192   # palm detector expects 192×192
LAND_INPUT_SIZE  = 224   # landmark model expects 224×224
PALM_CONF_THRESH = 0.50  # minimum palm-detection confidence
PALM_PAD         = 0.20  # fractional padding around the detected palm box


# ── Thin dataclass that mirrors mediapipe NormalizedLandmark ──────────────────
@dataclass
class Landmark:
    x: float   # [0, 1] relative to the crop (re-projected to full frame below)
    y: float
    z: float


@dataclass
class HandResult:
    """Wraps 21 Landmark objects — mirrors mediapipe's MultiHandLandmarks item."""
    landmark: list[Landmark]


# ── ONNX session loader (lazy, loaded once) ────────────────────────────────────
_palm_session:  Optional[ort.InferenceSession] = None
_land_session:  Optional[ort.InferenceSession] = None
_model_paths:   Optional[dict] = None


def _get_sessions() -> tuple[ort.InferenceSession, ort.InferenceSession]:
    global _palm_session, _land_session, _model_paths
    if _palm_session is None:
        _model_paths  = ensure_models()
        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 2
        _palm_session = ort.InferenceSession(
            str(_model_paths["palm"]), sess_options=opts
        )
        _land_session = ort.InferenceSession(
            str(_model_paths["landmark"]), sess_options=opts
        )
    return _palm_session, _land_session


# ── Pre-processing helpers ─────────────────────────────────────────────────────

def _preprocess(bgr_frame: np.ndarray, size: int) -> np.ndarray:
    """Resize + normalise a BGR frame to a (1, 3, size, size) float32 tensor."""
    rgb   = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (size, size), interpolation=cv2.INTER_LINEAR)
    tensor  = resized.astype(np.float32) / 255.0          # [0, 1]
    tensor  = np.transpose(tensor, (2, 0, 1))              # HWC → CHW
    return np.expand_dims(tensor, axis=0)                  # → (1, 3, H, W)


# ── Stage 1 : Palm detection ───────────────────────────────────────────────────

def _detect_palm(
    frame: np.ndarray,
    session: ort.InferenceSession,
) -> Optional[tuple[int, int, int, int]]:
    """
    Run the palm detector on `frame`.

    Returns the best bounding box as (x1, y1, x2, y2) in pixel coords,
    or None if no palm was found above PALM_CONF_THRESH.
    """
    h, w = frame.shape[:2]
    inp_name = session.get_inputs()[0].name
    tensor   = _preprocess(frame, PALM_INPUT_SIZE)
    outputs  = session.run(None, {inp_name: tensor})

    # This "_post" model bakes in decoding + NMS and returns ONE detections
    # array. The output name is the schema — each row is 8 values:
    #   outputs[1] shape (N, 8) = [score, cx, cy, w, wrist_x, wrist_y, mid_x, mid_y]
    #   outputs[0] is just batch indices — ignore it.
    dets = outputs[1]                       # (N, 8)
    if dets.shape[0] == 0:                  # no palms detected this frame
        return None

    best      = dets[int(np.argmax(dets[:, 0]))]   # row with the highest score
    best_conf = float(best[0])
    # DEBUG (remove later): shows whether the palm detector fires and what the
    # raw box values look like — tells us confidence + normalized-vs-pixel coords.
    print(f"[palm] n={dets.shape[0]} conf={best_conf:.2f} "
          f"cx={best[1]:.3f} cy={best[2]:.3f} w={best[3]:.3f}", flush=True)
    if best_conf < PALM_CONF_THRESH:
        return None

    cx, cy, bw = best[1], best[2], best[3]
    bh = bw                                 # palm detector box is square (single 'w')

    # Convert from normalised centre-format to pixel corner-format
    x1 = int((cx - bw / 2) * w)
    y1 = int((cy - bh / 2) * h)
    x2 = int((cx + bw / 2) * w)
    y2 = int((cy + bh / 2) * h)

    # Add padding so the landmark model sees the full hand including fingertips
    pad_x = int((x2 - x1) * PALM_PAD)
    pad_y = int((y2 - y1) * PALM_PAD)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)

    return x1, y1, x2, y2


# ── Stage 2 : Hand landmark extraction ────────────────────────────────────────

def _extract_landmarks(
    frame: np.ndarray,
    box: tuple[int, int, int, int],
    session: ort.InferenceSession,
) -> HandResult:
    """
    Crop `frame` to `box`, run the landmark model, and return a HandResult
    whose landmark coordinates are projected back to the full-frame scale.
    """
    x1, y1, x2, y2 = box
    h, w = frame.shape[:2]

    crop   = frame[y1:y2, x1:x2]
    inp_name = session.get_inputs()[0].name
    tensor   = _preprocess(crop, LAND_INPUT_SIZE)
    outputs  = session.run(None, {inp_name: tensor})

    # The landmark model's first output is shape (1, 63) → 21 × (x, y, z)
    # Coordinates are normalised to [0, 1] within the crop.
    raw = outputs[0].reshape(21, 3)

    crop_w = x2 - x1
    crop_h = y2 - y1

    landmarks = []
    for lx, ly, lz in raw:
        # Project from crop-relative [0,1] back to full-frame [0,1]
        full_x = (x1 + lx * crop_w) / w
        full_y = (y1 + ly * crop_h) / h
        landmarks.append(Landmark(x=float(full_x), y=float(full_y), z=float(lz)))

    return HandResult(landmark=landmarks)


# ── Drawing helper ─────────────────────────────────────────────────────────────

def _draw_landmarks(frame: np.ndarray, hand: HandResult) -> None:
    """Draw 21 keypoints and connecting lines on `frame` in-place."""
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]

    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 220, 0), 2, cv2.LINE_AA)
    for pt in pts:
        cv2.circle(frame, pt, 5, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, pt, 5, (0, 180, 0),      1, cv2.LINE_AA)


# ── Public helpers (unchanged API) ────────────────────────────────────────────

def write_gesture(gesture: str) -> None:
    """Write the current gesture to the shared STATE_FILE."""
    with open(STATE_FILE, "w") as f:
        f.write(gesture)


def read_gesture() -> str:
    """Read the current gesture from the shared STATE_FILE."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return f.read()
    return "UNKNOWN"


def distance(a: Landmark, b: Landmark) -> float:
    """Euclidean distance between two Landmark objects (x, y only)."""
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


def detect_gesture(hand: HandResult) -> str:
    """
    Classify the hand pose into FIST, OPEN_PALM, OK, or UNKNOWN.

    Uses the same landmark indices and thresholds as the original
    MediaPipe implementation — no logic changes required.
    """
    pinch      = distance(hand.landmark[4], hand.landmark[8]) < 0.05
    middle_up  = hand.landmark[12].y < hand.landmark[10].y
    ring_up    = hand.landmark[16].y < hand.landmark[14].y
    pinky_up   = hand.landmark[20].y < hand.landmark[18].y

    fingers_up = 0
    if hand.landmark[8].y  < hand.landmark[6].y:  fingers_up += 1
    if hand.landmark[12].y < hand.landmark[10].y: fingers_up += 1
    if hand.landmark[16].y < hand.landmark[14].y: fingers_up += 1
    if hand.landmark[20].y < hand.landmark[18].y: fingers_up += 1

    # OK sign: thumb-index pinch with the remaining fingers extended
    if pinch and middle_up and ring_up and pinky_up:
        return "OK"

    if fingers_up == 4:
        return "OPEN_PALM"
    elif fingers_up == 0:
        return "FIST"
    else:
        return "UNKNOWN"


# ── Camera abstraction ─────────────────────────────────────────────────────────

class Camera:
    """
    Thin capture wrapper that prefers Picamera2 (the libcamera stack the Pi 5
    CSI ribbon camera uses) and falls back to cv2.VideoCapture for USB webcams
    and dev machines. It mirrors the small slice of the cv2.VideoCapture API the
    loop needs — is_opened() / read() / release() — so run() barely changes.
    """

    def __init__(self, size: tuple[int, int] = (640, 480)) -> None:
        self._picam2 = None   # Picamera2 handle, when the CSI camera is used
        self._cap = None      # cv2.VideoCapture handle, when falling back

        try:
            from picamera2 import Picamera2
            self._picam2 = Picamera2()
            config = self._picam2.create_preview_configuration(
                main={"format": "RGB888", "size": size}
            )
            self._picam2.configure(config)
            self._picam2.start()
        except Exception as exc:
            # picamera2 not installed, or no CSI camera → try a normal webcam.
            print(f"Picamera2 unavailable ({exc}); falling back to cv2.VideoCapture(0)")
            self._cap = cv2.VideoCapture(0)

    def is_opened(self) -> bool:
        if self._picam2 is not None:
            return True
        return self._cap is not None and self._cap.isOpened()

    def read(self) -> tuple[bool, Optional[np.ndarray]]:
        """Return (ret, frame) like cv2.VideoCapture.read(); frame is BGR."""
        if self._picam2 is not None:
            frame = self._picam2.capture_array()   # (H, W, 3)
            # Picamera2's "RGB888" format actually yields channels in B,G,R
            # order in the numpy array — i.e. already BGR, which is what the
            # rest of the pipeline (cv2 drawing, cvtColor BGR2RGB, imshow)
            # expects. If your colours come out swapped, wrap this line in
            # cv2.cvtColor(frame, cv2.COLOR_RGB2BGR).
            return True, frame
        return self._cap.read()

    def release(self) -> None:
        if self._picam2 is not None:
            self._picam2.stop()
            self._picam2.close()
        elif self._cap is not None:
            self._cap.release()


# ── Main camera loop ───────────────────────────────────────────────────────────

def run() -> None:
    """Camera loop: detect gesture each frame, write it only when it changes."""
    palm_sess, land_sess = _get_sessions()   # triggers model download if needed

    cap          = Camera()
    if not cap.is_opened():
        print(
            "ERROR: could not open a camera.\n"
            "  - CSI ribbon camera (Pi 5): install Picamera2 with\n"
            "      sudo apt install -y python3-picamera2\n"
            "    and verify the camera with `rpicam-hello --list-cameras`.\n"
            "  - USB webcam: check `ls /dev/video*` and permissions.\n"
            "Gesture thread exiting."
        )
        cap.release()
        return

    last_gesture: Optional[str] = None
    prev_x:       Optional[float] = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        box = _detect_palm(frame, palm_sess)

        if box is not None:
            hand     = _extract_landmarks(frame, box, land_sess)
            wrist_x  = hand.landmark[0].x
            gesture  = detect_gesture(hand)

            _draw_landmarks(frame, hand)

            # ── Swipe detection (unchanged logic) ─────────────────────────
            if prev_x is not None:
                dx = wrist_x - prev_x
                if dx > 0.1:
                    write_gesture("Swipe Right")
                elif dx < -0.1:
                    write_gesture("Swipe Left")
            prev_x = wrist_x

            # ── Static gesture (write only on change) ─────────────────────
            if gesture != last_gesture:
                write_gesture(gesture)
                last_gesture = gesture
        else:
            prev_x = None
            if last_gesture != "NONE":
                write_gesture("NONE")
                last_gesture = "NONE"

        if os.environ.get("DISPLAY"):
            try:
                cv2.imshow("Gesture Recognition", frame)
                cv2.waitKey(1)
            except cv2.error as e:
                print(f"OpenCV display error: {e}")

    cap.release()
    # Only tear down GUI windows if we actually created any. On a headless
    # OpenCV build (no GTK, as on the Pi) destroyAllWindows() raises
    # "The function is not implemented", so guard it the same way as imshow.
    if os.environ.get("DISPLAY"):
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass


if __name__ == "__main__":
    run()