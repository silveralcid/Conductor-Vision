import vlc
import time
import threading


class AudioEngine:
    def __init__(self, filepath: str, ramp_time=0.35):
        """
        ramp_time = seconds for fade-ins, fade-outs, volume transitions
        """
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
        self.target_volume = 100       # 0–100 target
        self.current_volume = 100
        self.last_rate = 1.0
        self.running = True

        # Threading
        self.ramp_thread = None
        self.ramp_lock = threading.Lock()

    # =========================================================
    # INTERNAL RAMPING SYSTEM
    # =========================================================

    def _start_ramp(self, new_target: int):
        """Trigger new ramp animation for volume."""
        with self.ramp_lock:
            self.target_volume = max(0, min(100, int(new_target)))

        if self.ramp_thread is None or not self.ramp_thread.is_alive():
            self.ramp_thread = threading.Thread(target=self._ramp_loop, daemon=True)
            self.ramp_thread.start()

    def _ramp_loop(self):
        """Smoothly transition current_volume → target_volume."""
        steps = max(1, int(self.RAMP_TIME / 0.02))

        for _ in range(steps):
            if not self.running:
                return

            with self.ramp_lock:
                diff = self.target_volume - self.current_volume
                if abs(diff) < 1:
                    break

                # Smooth quarter-step toward target
                self.current_volume += diff * 0.25

                vol = max(0, min(100, int(self.current_volume)))
                self.player.audio_set_volume(vol)

            time.sleep(0.02)

        # Snap to exact target
        self.player.audio_set_volume(int(self.target_volume))
        self.current_volume = self.target_volume

    # =========================================================
    # BASIC PLAYBACK CONTROLS
    # =========================================================

    def play(self):
        """Fade in if starting/resuming."""
        if not self.ready:
            self.player.play()
            time.sleep(0.1)
            self.player.set_rate(self.last_rate)
            self.player.audio_set_volume(int(self.current_volume))
            self.ready = True
        else:
            self.player.play()

        # Fade in toward the target
        self._start_ramp(self.target_volume)

    def pause(self):
        """Fade out to 0, then pause."""
        self._start_ramp(0)

        def _pause():
            time.sleep(self.RAMP_TIME)
            self.player.pause()

        threading.Thread(target=_pause, daemon=True).start()

    def restart(self):
        """Restart from zero with a fade-in."""
        self.player.stop()
        self.ready = False

        # Reload fresh looped media
        self.media = self.instance.media_new(self.filepath)
        self.media.add_option(":input-repeat=-1")
        self.player.set_media(self.media)

        self.player.play()
        time.sleep(0.1)

        # Restore rate + fade in
        self.player.set_rate(self.last_rate)
        self._start_ramp(self.target_volume)

        self.ready = True

    # =========================================================
    # EXPRESSIVE VOLUME CONTROL
    # =========================================================

    def set_expressive_volume(self, gesture_value: float):
        """
        gesture_value: 0.0 → 1.0
        Maps to:
            0.0 → ~35%
            0.5 → ~70%
            1.0 → 100%
        """
        gesture_value = max(0.0, min(1.0, gesture_value))

        multiplier = 0.5 + gesture_value      # → 0.5→1.5
        raw = multiplier * 70                # → 35→105 approx
        new_vol = max(35, min(100, int(raw)))

        self._start_ramp(new_vol)

    # =========================================================
    # TEMPO CONTROL (rate)
    # =========================================================

    def set_rate(self, rate: float):
        """
        Tempo changes are immediate (no ramp).
        Using VLC-safe range: 0.5x – 2.0x
        """
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
