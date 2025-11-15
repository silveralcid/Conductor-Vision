import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
from collections import deque
import time
from mediapipe.framework.formats import landmark_pb2

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


model_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "models",
        "hand_landmarker.task"
    )
)

def normalize_landmarks(landmarks_21):
    # landmarks_21 = [(x,y,z), ...] of length 21

    # Use wrist as origin (landmark 0)
    wrist_x, wrist_y, wrist_z = landmarks_21[0]

    normalized = []
    for (x, y, z) in landmarks_21:
        nx = x - wrist_x
        ny = y - wrist_y
        nz = z - wrist_z
        normalized.append((nx, ny, nz))

    # Optional: scale normalization (distance wrist → middle finger MCP)
    scale_ref = landmarks_21[9]  # index 9 = landmark on middle finger
    dist = abs(scale_ref[1] - wrist_y) + 1e-6

    scaled = [(nx / dist, ny / dist, nz / dist) for (nx, ny, nz) in normalized]
    return scaled


class LandmarkBuffer:
    def __init__(self, max_seconds=2.0):
        self.max_seconds = max_seconds
        self.buffer = deque()  # stores (timestamp, landmarks)

    def add(self, landmarks):
        timestamp = time.time()
        self.buffer.append((timestamp, landmarks))

        # Purge old entries
        while self.buffer and timestamp - self.buffer[0][0] > self.max_seconds:
            self.buffer.popleft()

    def get_sequence(self):
        return [entry[1] for entry in self.buffer]


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

    cap = cv2.VideoCapture(0)

    prev_time = time.time()
    fps = 0

    left_px = left_py = None
    right_px = right_py = None
    sequence = []
    bufsize = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run hand landmark detection
        result = landmarker.detect(mp_image)

        # Reset per-frame positions
        left_px = left_py = None
        right_px = right_py = None

        if result.hand_landmarks:
            hands_xy = {}

            for idx, hand in enumerate(result.hand_landmarks):

                # Convert to raw landmark list
                raw_landmarks = [(lm.x, lm.y, lm.z) for lm in hand]

                # Normalize + buffer
                normalized = normalize_landmarks(raw_landmarks)
                buffer.add(normalized)

                # Wrist → pixel coords
                h, w, _ = frame.shape
                wrist = raw_landmarks[0]
                px = int(wrist[0] * w)
                py = int(wrist[1] * h)

                # Left/Right label
                label = result.handedness[idx][0].category_name
                hands_xy[label] = (px, py)

                # Convert Task landmarks → Solutions NormalizedLandmarkList
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

                # Optional: Draw bigger wrist dot for clarity
                cv2.circle(
                    frame,
                    (px, py),
                    10,
                    (0, 255, 0) if label == "Left" else (255, 0, 0),
                    -1
                )


            left_px, left_py = hands_xy.get("Left", (None, None))
            right_px, right_py = hands_xy.get("Right", (None, None))

        # Always update buffer size (even if no hands)
        sequence = buffer.get_sequence()
        bufsize = len(sequence)

        # ----------------------------
        # Persistent Debug Overlay
        # ----------------------------
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        cv2.putText(frame, f"Buffer: {bufsize}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

        # Left hand
        if left_px is not None:
            cv2.putText(frame, f"L: ({left_px}, {left_py})", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        else:
            cv2.putText(frame, "L: ---", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Right hand
        if right_px is not None:
            cv2.putText(frame, f"R: ({right_px}, {right_py})", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
        else:
            cv2.putText(frame, "R: ---", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

        # FPS update
        current_time = time.time()
        fps = 1.0 / (current_time - prev_time)
        prev_time = current_time

        cv2.imshow("Conductor Vision - Wrist Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
