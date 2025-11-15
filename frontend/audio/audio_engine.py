# conductor-vision/frontend/audio/audio_engine.py

import vlc
import time


class AudioEngine:
    def __init__(self, filepath: str):
        """
        Minimal VLC audio engine:
        - Auto-loops forever (input-repeat = -1)
        - play()     → start or resume
        - pause()    → pause at current position
        - restart()  → reset to beginning
        """
        self.filepath = filepath

        # Create VLC instance
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()

        # Load media with loop option
        self.media = self.instance.media_new(filepath)
        self.media.add_option(":input-repeat=-1")   # infinite loop
        self.player.set_media(self.media)

        self.last_rate = 1.0
        self.current_volume = 100   # VLC uses 0–100
        self.ready = False          # becomes True after first play()

    # ---------------------------------------------------------
    # BASIC PLAYBACK CONTROLS
    # ---------------------------------------------------------

    def play(self):
        """
        Start or resume playback.
        Ensures initialization happens once.
        """
        if not self.ready:
            self.player.play()
            time.sleep(0.1)  # allow VLC to initialize
            self.player.set_rate(self.last_rate)
            self.player.audio_set_volume(self.current_volume)
            self.ready = True
        else:
            self.player.play()

    def pause(self):
        """Pause playback (keeps current position)."""
        self.player.pause()

    def restart(self):
        """
        Restart from absolute 0.0.
        Reloads media so VLC doesn't start slightly offset.
        """
        self.player.stop()
        self.ready = False

        # Reload media fresh (still looped)
        self.media = self.instance.media_new(self.filepath)
        self.media.add_option(":input-repeat=-1")
        self.player.set_media(self.media)

        # Start again from the beginning
        self.player.play()
        time.sleep(0.1)
        self.player.set_rate(self.last_rate)
        self.player.audio_set_volume(self.current_volume)

        self.ready = True

    # ---------------------------------------------------------
    # CONTROL PROPERTIES
    # ---------------------------------------------------------

    def set_volume(self, vol_0_to_1: float):
        """Convert 0.0–1.0 → VLC 0–100."""
        vol = int(max(0.0, min(1.0, vol_0_to_1)) * 100)
        self.current_volume = vol
        self.player.audio_set_volume(vol)

    def set_rate(self, rate: float):
        """Change playback speed safely."""
        rate = max(0.5, min(2.0, rate))
        self.last_rate = rate
        try:
            self.player.set_rate(rate)
        except:
            pass  # VLC rejects rate changes if paused

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def is_playing(self) -> bool:
        return self.player.is_playing() == 1


    def set_expressive_volume(self, gesture_value: float):
        """
        gesture_value: 0.0 → 1.0 (from vision model)
        baseline: 0.5 = neutral music loudness

        Mapping:
        0.0 → 0.5x loudness
        0.5 → 1.0x loudness
        1.0 → 1.5x loudness
        """
        gesture_value = max(0.0, min(1.0, gesture_value))

        # multiplier from ~0.5 → ~1.5
        multiplier = 0.5 + gesture_value

        # map to VLC scale (0–100), baseline ~70
        raw_volume = int(multiplier * 70)
        raw_volume = max(35, min(100, raw_volume))   # safe, no silence

        self.current_volume = raw_volume
        self.player.audio_set_volume(raw_volume)
