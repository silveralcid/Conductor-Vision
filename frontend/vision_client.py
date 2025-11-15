import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

# model_path = os.path.join(
#     os.path.dirname(__file__),
#     "models",
#     "hand_landmarker.task"
# )

model_path = r"C:\mediapipe_test\hand_landmarker.task"


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

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run hand landmark detection
        result = landmarker.detect(mp_image)

        if result.hand_landmarks:
            for hand in result.hand_landmarks:
                # wrist = landmark index 0
                wrist = hand[0]
                h, w, _ = frame.shape
                px = int(wrist.x * w)
                py = int(wrist.y * h)

                # Draw wrist dot
                cv2.circle(frame, (px, py), 10, (0, 255, 0), -1)

        cv2.imshow("Conductor Vision - Wrist Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
