# conductor-vision/frontend/controls/volume.py

import math

class VolumeControl:
    def __init__(self, min_dist=40, max_dist=600):
        """
        min_dist = hands almost touching (volume = 0)
        max_dist = arms stretched apart (volume = 1)
        """
        self.min_dist = min_dist
        self.max_dist = max_dist

    def compute(self, lx, ly, rx, ry):
        if None in (lx, ly, rx, ry):
            return None

        dist = math.sqrt((rx - lx)**2 + (ry - ly)**2)
        dist = max(self.min_dist, min(self.max_dist, dist))
        return (dist - self.min_dist) / (self.max_dist - self.min_dist)
