# conductor-vision/frontend/capture/hand_tracker.py

import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class HandTracker:
    def __init__(self, landmarker):
        self.landmarker = landmarker

    def detect(self, mp_image, frame):
        result = self.landmarker.detect(mp_image)
        h, w, _ = frame.shape
        hands_xy = {}
        raw_hands = []

        if not result.hand_landmarks:
            return hands_xy, raw_hands

        for idx, hand in enumerate(result.hand_landmarks):
            raw = [(lm.x, lm.y, lm.z) for lm in hand]
            raw_hands.append(raw)

            wrist = raw[0]
            px = int(wrist[0] * w)
            py = int(wrist[1] * h)

            label = result.handedness[idx][0].category_name
            hands_xy[label] = (px, py)

            lm_list = landmark_pb2.NormalizedLandmarkList()
            for lm in hand:
                lm_list.landmark.add(x=lm.x, y=lm.y, z=lm.z)

            mp_drawing.draw_landmarks(
                frame,
                lm_list,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(255,255,255), thickness=2),
            )

        return hands_xy, raw_hands
