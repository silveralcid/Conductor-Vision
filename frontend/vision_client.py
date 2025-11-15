# conductor-vision/frontend/vision_client.py

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import time

from capture.normalize import normalize_landmarks
from capture.buffer import LandmarkBuffer
from capture.recorder import Recorder
from capture.hand_tracker import HandTracker

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "hand_landmarker.task")
)

RECORD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "recordings")
)

def main():
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    landmarker = vision.HandLandmarker.create_from_options(options)
    tracker = HandTracker(landmarker)

    buffer = LandmarkBuffer(max_seconds=2.0)
    recorder = Recorder(RECORD_DIR)

    cap = cv2.VideoCapture(0)

    prev_time = time.time()
    fps = 0
    left_px = left_py = None
    right_px = right_py = None

    while True:
        key = cv2.waitKey(1) & 0xFF

        if key == ord("r"):
            recorder.toggle()

        if key == ord("q"):
            break

        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        hands_xy, raw_hands = tracker.detect(mp_image, frame)

        left_px, left_py = hands_xy.get("Left", (None, None))
        right_px, right_py = hands_xy.get("Right", (None, None))

        if raw_hands:
            normalized = normalize_landmarks(raw_hands[0])
            buffer.add(normalized)
            recorder.add(normalized)

        bufsize = len(buffer.get_sequence())

        # --- Visual overlay ---
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.putText(frame, f"Buffer: {bufsize}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

        cv2.putText(frame, f"L: {left_px, left_py}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(frame, f"R: {right_px, right_py}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

        status_color = (0,0,255) if recorder.recording else (100,100,100)
        cv2.putText(frame, "REC", (10,150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

        # FPS calc
        now = time.time()
        fps = 1.0 / (now - prev_time)
        prev_time = now

        cv2.imshow("Conductor Vision - Wrist Tracking", frame)

    cap.release()
    recorder.save()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
