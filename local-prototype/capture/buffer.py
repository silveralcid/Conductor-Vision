# conductor-vision/frontend/capture/buffer.py

from collections import deque
import time

class LandmarkBuffer:
    def __init__(self, max_seconds=2.0):
        self.max_seconds = max_seconds
        self.buffer = deque()

    def add(self, landmarks):
        timestamp = time.time()
        self.buffer.append((timestamp, landmarks))
        while self.buffer and timestamp - self.buffer[0][0] > self.max_seconds:
            self.buffer.popleft()

    def get_sequence(self):
        return [entry[1] for entry in self.buffer]
