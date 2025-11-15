# conductor-vision/frontend/capture/recorder.py

import os
import json
from datetime import datetime

class Recorder:
    def __init__(self, base_dir):
        self.recording = False
        self.frames = []
        self.out_path = None
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def toggle(self):
        self.recording = not self.recording

        if self.recording:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.out_path = os.path.join(self.base_dir, f"recording_{timestamp}.json")
            self.frames = []
            print(f"[REC START] → {self.out_path}")
        else:
            print("[REC STOP]")

    def add(self, normalized_frame):
        if self.recording:
            self.frames.append(normalized_frame)

    def save(self):
        if self.frames and self.out_path:
            with open(self.out_path, "w") as f:
                json.dump(self.frames, f, indent=2)
            print(f"[SAVED] {len(self.frames)} frames → {self.out_path}")
