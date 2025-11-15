# conductor-vision/frontend/controls/tempo.py

class TempoControl:
    def __init__(self, min_bpm=80, max_bpm=160, min_rate=0.8, max_rate=1.2):
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        self.min_rate = min_rate
        self.max_rate = max_rate

        self.last_rate = 1.0   # fallback when BPM missing

    def compute_rate(self, bpm):
        """
        Convert gesture BPM into playback speed inside a safe expressive range.
        """

        if bpm is None:
            # no BPM detected → return last stable rate
            return self.last_rate

        # clamp BPM
        bpm = max(self.min_bpm, min(self.max_bpm, bpm))

        # map BPM → 0..1
        t = (bpm - self.min_bpm) / (self.max_bpm - self.min_bpm)

        # map into playback speed range
        rate = self.min_rate + t * (self.max_rate - self.min_rate)

        # smooth a bit (optional)
        smoothed = 0.2 * rate + 0.8 * self.last_rate

        self.last_rate = smoothed
        return smoothed
