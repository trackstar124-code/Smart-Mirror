"""
inspect_palm_model.py
~~~~~~~~~~~~~~~~~~~~~~
Throwaway diagnostic: prints the real input/output shapes of the palm-detection
ONNX model so we can fix _detect_palm() to match. Safe to delete afterwards.

Run from the smart-mirror/ directory:
    python app/modules/inspect_palm_model.py
"""

import numpy as np
import onnxruntime as ort
from pathlib import Path

MODEL = Path(__file__).parent / "models" / "palm_detection_full_Nx3x192x192_post.onnx"

sess = ort.InferenceSession(str(MODEL))

print("── declared inputs ──")
for i in sess.get_inputs():
    print(f"  {i.name:20s} {i.shape}")

print("── declared outputs ──")
for o in sess.get_outputs():
    print(f"  {o.name:20s} {o.shape}")

# Run one inference on a blank frame to see the concrete shapes.
dummy = np.zeros((1, 3, 192, 192), dtype=np.float32)
outs = sess.run(None, {sess.get_inputs()[0].name: dummy})

print("── actual output shapes ──")
for idx, arr in enumerate(outs):
    print(f"  outputs[{idx}]  shape={arr.shape}  dtype={arr.dtype}")
