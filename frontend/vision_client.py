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
        # OVERLAY
        # ====================================================
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

        # BPM
        if bpm is not None:
            cv2.putText(frame, f"BPM: {bpm:.1f}", (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,200,255), 2)
        else:
            cv2.putText(frame, "BPM: --", (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100,100,100), 2)

        # Volume (raw gesture)
        if volume is not None:
            cv2.putText(frame, f"VOL: {volume:.2f}", (10, 210),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,150,255), 2)
        else:
            cv2.putText(frame, "VOL: --", (10, 210),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100,100,100), 2)

        # MUSIC STATE
        music_status = "PLAYING" if audio.is_playing() else "PAUSED"
        cv2.putText(frame, f"MUSIC: {music_status}", (10, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,200,255), 2)

        # RATE
        cv2.putText(frame, f"RATE: {playback_rate:.2f}x", (10, 270),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,200,0), 2)

        # DEBUG FLAGS
        cv2.putText(frame, f"VOLCTL: {'ON' if volume_enabled else 'OFF'}",
                    (10, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0,255,180) if volume_enabled else (80,80,80), 2)

        cv2.putText(frame, f"TEMPOCTL: {'ON' if tempo_enabled else 'OFF'}",
                    (10, 330),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255,180,0) if tempo_enabled else (80,80,80), 2)

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
