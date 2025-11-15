import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
from collections import deque
import time
from mediapipe.framework.formats import landmark_pb2
import json
from datetime import datetime

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# ----------------------------------------------------------------------
# Model path
# ----------------------------------------------------------------------
model_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "models",
        "hand_landmarker.task"
    )
)

# ----------------------------------------------------------------------
# Recording directory
# ----------------------------------------------------------------------
RECORD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "recordings")
)
os.makedirs(RECORD_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# Normalization
# ----------------------------------------------------------------------
def normalize_landmarks(landmarks_21):
    wrist_x, wrist_y, wrist_z = landmarks_21[0]

    normalized = []
    for (x, y, z) in landmarks_21:
        nx = x - wrist_x
        ny = y - wrist_y
        nz = z - wrist_z
        normalized.append((nx, ny, nz))

    scale_ref = landmarks_21[9]
    dist = abs(scale_ref[1] - wrist_y) + 1e-6

    scaled = [(nx / dist, ny / dist, nz / dist) for (nx, ny, nz) in normalized]
    return scaled

# ----------------------------------------------------------------------
# Rolling buffer (2 seconds)
# ----------------------------------------------------------------------
class LandmarkBuffer:
    def __init__(self, max_seconds=2.0):
        self.max_seconds = max_seconds
        self.buffer = deque()

    def add(self, landmarks):
        timestamp = time.time()
        self.buffer.append((timestamp, landmarks))
        while self.buffer and timestamp - self.buffer[0][0] > self.max_seconds:
            self.buffer.popleft()

    def get_sequence(self):
        return [entry[1] for entry in self.buffer]

# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    base_options = python.BaseOptions(model_asset_path=model_path)

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    landmarker = vision.HandLandmarker.create_from_options(options)
    buffer = LandmarkBuffer(max_seconds=2.0)

    recording = False
    recorded_frames = []  # store only normalized frames when recording ON

    cap = cv2.VideoCapture(0)

    prev_time = time.time()
    fps = 0

    left_px = left_py = None
    right_px = right_py = None
    sequence = []
    bufsize = 0

    # Path for output file (set only on recording start)
    out_path = None

    while True:
        key = cv2.waitKey(1) & 0xFF

        # Toggle recording
        if key == ord('r'):
            recording = not recording

            if recording:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_path = os.path.join(RECORD_DIR, f"recording_{timestamp}.json")
                recorded_frames = []  # reset buffer
                print(f"[REC START] → {out_path}")
            else:
                print("[REC STOP]")

        # Quit
        if key == ord('q'):
            break

        # Read frame
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Inference
        result = landmarker.detect(mp_image)

        left_px = left_py = None
        right_px = right_py = None

        if result.hand_landmarks:
            hands_xy = {}

            for idx, hand in enumerate(result.hand_landmarks):
                raw_landmarks = [(lm.x, lm.y, lm.z) for lm in hand]

                normalized = normalize_landmarks(raw_landmarks)
                buffer.add(normalized)

                # Wrist pixel
                h, w, _ = frame.shape
                wrist = raw_landmarks[0]
                px = int(wrist[0] * w)
                py = int(wrist[1] * h)

                label = result.handedness[idx][0].category_name
                hands_xy[label] = (px, py)

                # Convert task landmarks to drawing protobuf
                lm_list = landmark_pb2.NormalizedLandmarkList()
                for lm in hand:
                    lm_list.landmark.add(x=lm.x, y=lm.y, z=lm.z)

                # Draw skeleton
                mp_drawing.draw_landmarks(
                    frame,
                    lm_list,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
                    mp_drawing.DrawingSpec(color=(255,255,255), thickness=2),
                )

                # Emphasize wrist
                cv2.circle(frame, (px, py), 10,
                           (0,255,0) if label == "Left" else (255,0,0),
                           -1)

            left_px, left_py = hands_xy.get("Left", (None, None))
            right_px, right_py = hands_xy.get("Right", (None, None))

        # Update buffer state
        sequence = buffer.get_sequence()
        bufsize = len(sequence)

        # Store normalized frame when recording
        if recording and sequence:
            recorded_frames.append(sequence[-1])  # append latest normalized frame

        # ------------------------------------------------------------------
        # Debug overlay
        # ------------------------------------------------------------------
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        cv2.putText(frame, f"Buffer: {bufsize}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

        if left_px is not None:
            cv2.putText(frame, f"L: ({left_px}, {left_py})", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        else:
            cv2.putText(frame, "L: ---", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        if right_px is not None:
            cv2.putText(frame, f"R: ({right_px}, {right_py})", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
        else:
            cv2.putText(frame, "R: ---", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

        # Recording indicator
        status_color = (0,0,255) if recording else (100,100,100)
        cv2.putText(frame, "REC", (10,150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

        # FPS
        current_time = time.time()
        fps = 1.0 / (current_time - prev_time)
        prev_time = current_time

        cv2.imshow("Conductor Vision - Wrist Tracking", frame)

    # ------------------------------------------------------------------
    # Save recording if any
    # ------------------------------------------------------------------
    cap.release()

    if recording:
        print("[REC STOP automatically on quit]")

    if recorded_frames and out_path:
        with open(out_path, "w") as f:
            json.dump(recorded_frames, f, indent=2)
        print(f"[SAVED] {len(recorded_frames)} frames → {out_path}")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
