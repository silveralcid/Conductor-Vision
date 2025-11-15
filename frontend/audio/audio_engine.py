import vlc
import time
import threading


class AudioEngine:
    def __init__(self, filepath: str, ramp_time=10):
        self.filepath = filepath
        self.RAMP_TIME = ramp_time

        # VLC setup
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()

        # Loop audio forever
        self.media = self.instance.media_new(filepath)
        self.media.add_option(":input-repeat=-1")
        self.player.set_media(self.media)

        # State
        self.ready = False
        self.target_volume = 100
        self.current_volume = 100
        self.last_rate = 1.0
        self.running = True
        self.is_fading = False     # NEW

        # Threading
        self.ramp_thread = None
        self.ramp_lock = threading.Lock()

    # =========================================================
    # INTERNAL RAMPING SYSTEM
    # =========================================================

    def _start_ramp(self, new_target: int):
        """Trigger new ramp animation."""
        with self.ramp_lock:
            self.target_volume = max(0, min(100, int(new_target)))
            self.is_fading = True

        if self.ramp_thread is None or not self.ramp_thread.is_alive():
            self.ramp_thread = threading.Thread(target=self._ramp_loop, daemon=True)
            self.ramp_thread.start()

    def _ramp_loop(self):
        steps = max(1, int(self.RAMP_TIME / 0.02))

        for _ in range(steps):
            if not self.running:
                return

            with self.ramp_lock:
                diff = self.target_volume - self.current_volume
                if abs(diff) < 1:
                    break

                self.current_volume += diff * 0.25
                vol = max(0, min(100, int(self.current_volume)))
                self.player.audio_set_volume(vol)

            time.sleep(0.02)

        # Final snap
        self.player.audio_set_volume(int(self.target_volume))
        self.current_volume = self.target_volume

        with self.ramp_lock:
            self.is_fading = False

    # =========================================================
    # BASIC CONTROLS
    # =========================================================

    def play(self):
        """Smooth fade-in."""
        # Always reset volume to 0 BEFORE playing
        self.player.audio_set_volume(0)
        self.current_volume = 0

        if not self.ready:
            self.player.play()
            time.sleep(0.1)
            self.player.set_rate(self.last_rate)
            self.ready = True
        else:
            self.player.play()

        # fade to target
        self._start_ramp(self.target_volume)

    def pause(self):
        """Fade to 0, THEN pause cleanly."""
        self._start_ramp(0)

        def finish_pause():
            # Wait until volume reaches 0
            while True:
                with self.ramp_lock:
                    if self.current_volume <= 1:   # effectively silent
                        break
                time.sleep(0.02)

            # Now safe to pause — no audible click
            self.player.pause()

        threading.Thread(target=finish_pause, daemon=True).start()


    def restart(self):
        """Restart track from time 0 with a fade-in."""
        self.player.stop()
        self.ready = False

        self.media = self.instance.media_new(self.filepath)
        self.media.add_option(":input-repeat=-1")
        self.player.set_media(self.media)

        # Always start silent
        self.player.audio_set_volume(0)
        self.current_volume = 0

        self.player.play()
        time.sleep(0.1)

        self.player.set_rate(self.last_rate)
        self._start_ramp(self.target_volume)

        self.ready = True

    # =========================================================
    # EXPRESSIVE VOLUME
    # =========================================================

    def set_expressive_volume(self, gesture_value: float):
        gesture_value = max(0.0, min(1.0, gesture_value))
        multiplier = 0.5 + gesture_value
        raw = multiplier * 70
        new_vol = max(35, min(100, int(raw)))
        self._start_ramp(new_vol)

    # =========================================================
    # RATE CONTROL
    # =========================================================

    def set_rate(self, rate: float):
        rate = max(0.5, min(2.0, rate))
        self.last_rate = rate
        try:
            self.player.set_rate(rate)
        except:
            pass

    # =========================================================
    # STATUS
    # =========================================================

    def is_playing(self) -> bool:
        return self.player.is_playing() == 1

    def shutdown(self):
        self.running = False
