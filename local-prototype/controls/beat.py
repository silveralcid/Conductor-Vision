# conductor-vision/frontend/controls/beat.py

import time

class BeatDetector:
    def __init__(self):
        self.last_y = None
        self.last_downbeat_time = None
        self.ema_bpm = None

        # thresholds
        self.min_interval = 0.25       # sec → max 240 BPM
        self.velocity_threshold = 4     # minimum downward movement
        self.reverse_velocity_limit = -6  # upward too fast = reset

        # EMA smoothing
        self.alpha = 0.25

    def update(self, y):
        """
        Feed right-hand Y pixel coordinate each frame.
        Returns BPM or None.
        """

        now = time.time()

        # First frame
        if self.last_y is None:
            self.last_y = y
            return self.ema_bpm

        # Compute vertical velocity (+ = downward because screen coords)
        velocity = y - self.last_y
        self.last_y = y

        # If hand jumps upward violently → reset
        if velocity < self.reverse_velocity_limit:
            return self.ema_bpm

        # Beat = sharp downward motion
        if velocity > self.velocity_threshold:
            # Refractory period: avoid double-counting
            if self.last_downbeat_time is not None:
                if (now - self.last_downbeat_time) < self.min_interval:
                    return self.ema_bpm

            # A valid downbeat
            if self.last_downbeat_time is not None:
                interval = now - self.last_downbeat_time
                bpm = 60.0 / interval
                bpm = max(40, min(200, bpm))  # clamp

                # Smooth BPM
                if self.ema_bpm is None:
                    self.ema_bpm = bpm
                else:
                    self.ema_bpm = (
                        self.alpha * bpm + (1 - self.alpha) * self.ema_bpm
                    )

            self.last_downbeat_time = now

        return self.ema_bpm
