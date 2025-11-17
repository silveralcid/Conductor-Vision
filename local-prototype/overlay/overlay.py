# conductor-vision/frontend/overlay/overlay.py

import cv2
import time

def draw_overlay(frame, info):
    """
    info: dictionary containing:
        fps, bufsize,
        left_px, left_py,
        right_px, right_py,
        recorder, bpm, volume,
        music_status, playback_rate,
        volume_enabled, tempo_enabled,
        last_volume_time, volume_timeout
    """

    # Shortcuts
    fps = info["fps"]
    buf = info["bufsize"]
    lpx, lpy = info["left_px"], info["left_py"]
    rpx, rpy = info["right_px"], info["right_py"]

    recorder = info["recorder"]
    bpm = info["bpm"]
    volume = info["volume"]

    music_status = info["music_status"]
    playback_rate = info["rate"]

    volume_enabled = info["volume_enabled"]
    tempo_enabled = info["tempo_enabled"]

    last_volume_time = info["last_volume_time"]
    volume_timeout = info["volume_timeout"]

    # ------------------------------------------------------------------
    # TEXT OVERLAY
    # ------------------------------------------------------------------

    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.putText(frame, f"Buffer: {buf}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

    cv2.putText(frame, f"L: {lpx, lpy}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.putText(frame, f"R: {rpx, rpy}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

    # Recording indicator
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

    # Volume (gesture raw)
    if volume is not None:
        cv2.putText(frame, f"VOL: {volume:.2f}", (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,150,255), 2)
    else:
        cv2.putText(frame, "VOL: --", (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100,100,100), 2)

    cv2.putText(frame, f"MUSIC: {music_status}", (10, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,200,255), 2)

    cv2.putText(frame, f"RATE: {playback_rate:.2f}x", (10, 270),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,200,0), 2)

    # Debug flags
    cv2.putText(
        frame,
        f"VOLCTL: {'ON' if volume_enabled else 'OFF'}",
        (10, 300),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0,255,180) if volume_enabled else (80,80,80),
        2
    )

    cv2.putText(
        frame,
        f"TEMPOCTL: {'ON' if tempo_enabled else 'OFF'}",
        (10, 330),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,180,0) if tempo_enabled else (80,80,80),
        2
    )

    # Auto-pause indicator
    if (time.time() - last_volume_time) > volume_timeout:
        cv2.putText(frame, "AUTO-PAUSED", (10, 360),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,100,255), 2)
    else:
        cv2.putText(frame, "ACTIVE", (10, 360),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,100), 2)
