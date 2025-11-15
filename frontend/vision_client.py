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

from controls.beat import BeatDetector
from controls.volume import VolumeControl
from controls.tempo import TempoControl

from audio.audio_engine import AudioEngine
from overlay.overlay import draw_overlay



MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "hand_landmarker.task")
)

RECORD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "recordings")
)

MUSIC_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "music", "music.mp3")
)


def main():

    last_volume_time = time.time()
    tempo_control = TempoControl()

    VOLUME_TIMEOUT = 2.0   # seconds of no volume input → pause

    # ---------------------------------------------------------
    # DEBUG FLAGS + DEFAULTS
    # ---------------------------------------------------------
    volume_enabled = True
    tempo_enabled = True

    DEFAULT_VOLUME = 0.5     # expressive baseline
    DEFAULT_RATE = 1.0       # normal track speed

    # ---------------------------------------------------------
    # Control logic
    # ---------------------------------------------------------
    beat_detector = BeatDetector()
    volume_control = VolumeControl()

    # ---------------------------------------------------------
    # Audio engine
    # ---------------------------------------------------------
    audio = AudioEngine(MUSIC_PATH)

    # ---------------------------------------------------------
    # MediaPipe
    # ---------------------------------------------------------
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

    bpm = None
    volume = None
    left_px = left_py = None
    right_px = right_py = None

    # ============================================================
    # MAIN LOOP
    # ============================================================
    while True:

        key = cv2.waitKey(1) & 0xFF

        # Toggle recording
        if key == ord("r"):
            recorder.toggle()

        # SPACE → Play/Pause
        if key == ord(" "):
            if audio.is_playing():
                audio.pause()
            else:
                audio.play()

        # S → Restart
        if key == ord("s"):
            audio.restart()

        # ---------------------------------------------------------
        # DEBUG TOGGLES
        # ---------------------------------------------------------
        if key == ord("v"):
            volume_enabled = not volume_enabled
            # On toggle → snap to default volume
            audio.set_expressive_volume(DEFAULT_VOLUME)
            last_volume_time = time.time()

        if key == ord("t"):
            tempo_enabled = not tempo_enabled
            # On toggle → restore default rate
            audio.set_rate(DEFAULT_RATE)

        # Quit
        if key == ord("q"):
            break

        # ---------------------------------------------------------
        # Camera + Hand Tracking
        # ---------------------------------------------------------
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        hands_xy, raw_hands = tracker.detect(mp_image, frame)

        left_px, left_py = hands_xy.get("Left", (None, None))
        right_px, right_py = hands_xy.get("Right", (None, None))

        # Normalize + record
        if raw_hands:
            normalized = normalize_landmarks(raw_hands[0])
            buffer.add(normalized)
            recorder.add(normalized)

        bufsize = len(buffer.get_sequence())

        # ---------------------------------------------------------
        # BEAT DETECTION → BPM
        # ---------------------------------------------------------
        if right_py is not None:
            bpm = beat_detector.update(right_py)

        # ---------------------------------------------------------
        # TEMPO CONTROL
        # ---------------------------------------------------------
        playback_rate = tempo_control.compute_rate(bpm)

        if tempo_enabled:
            audio.set_rate(playback_rate)
        else:
            audio.set_rate(DEFAULT_RATE)

        # ---------------------------------------------------------
        # VOLUME CONTROL
        # ---------------------------------------------------------
        volume = volume_control.compute(left_px, left_py, right_px, right_py)

        if volume_enabled and volume is not None:
            audio.set_expressive_volume(volume)
            last_volume_time = time.time()

            if not audio.is_playing():
                audio.play()

        elif volume_enabled:
            # If no input for too long → auto pause
            if time.time() - last_volume_time > VOLUME_TIMEOUT:
                if audio.is_playing():
                    audio.pause()
        else:
            # Volume control OFF → enforce default baseline
            audio.set_expressive_volume(DEFAULT_VOLUME)

       # ====================================================
       # OVERLAY (refactored)
       # ====================================================
        draw_overlay(frame, {
            "fps": fps,
            "bufsize": bufsize,
            "left_px": left_px, "left_py": left_py,
            "right_px": right_px, "right_py": right_py,
            "recorder": recorder,
            "bpm": bpm,
            "volume": volume,
            "music_status": "PLAYING" if audio.is_playing() else "PAUSED",
            "rate": playback_rate,
            "volume_enabled": volume_enabled,
            "tempo_enabled": tempo_enabled,
            "last_volume_time": last_volume_time,
            "volume_timeout": VOLUME_TIMEOUT,
        })


        # FPS update
        now = time.time()
        fps = 1.0 / (now - prev_time)
        prev_time = now

        cv2.imshow("Conductor Vision", frame)

    cap.release()
    recorder.save()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
