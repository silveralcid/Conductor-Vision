# conductor-vision/frontend/controls/tempo.py

import time

class TempoControl:
    def __init__(
        self,
        min_bpm=80,
        max_bpm=160,
        min_rate=0.75,
        max_rate=1.25,
        deadband=0.002,  
        update_interval=0.15
    ):
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        self.min_rate = min_rate
        self.max_rate = max_rate

        self.deadband = deadband
        self.update_interval = update_interval

        self.last_rate = 1.0
        self.last_vlc_update_time = 0

    def compute_rate(self, bpm):
        now = time.time()

        # keep previous if no BPM
        if bpm is None:
            return self.last_rate

        # clamp BPM
        bpm = max(self.min_bpm, min(self.max_bpm, bpm))

        # map BPM → 0..1
        t = (bpm - self.min_bpm) / (self.max_bpm - self.min_bpm)

        # map to playback rate
        rate = self.min_rate + t * (self.max_rate - self.min_rate)

        # smooth
        smoothed = 0.35 * rate + 0.65 * self.last_rate

        # deadband
        if abs(smoothed - self.last_rate) < self.deadband:
            return self.last_rate

        # throttle
        if now - self.last_vlc_update_time < self.update_interval:
            return self.last_rate

        # accept new rate
        self.last_vlc_update_time = now
        self.last_rate = smoothed
        return smoothed
