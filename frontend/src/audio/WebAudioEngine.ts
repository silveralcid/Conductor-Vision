// frontend / src / audio / WebAudioEngine.ts;

export class WebAudioEngine {
  private audioCtx: AudioContext;
  private source: AudioBufferSourceNode | null = null;
  private gainNode: GainNode;
  private buffer: AudioBuffer | null = null;

  private targetVolume = 1.0;
  private currentVolume = 1.0;

  private rampTime: number;
  private rate = 1.0;

  private isPlaying = false;
  private rafId: number | null = null;

  constructor(rampTime = 1.0) {
    this.audioCtx = new AudioContext();
    this.gainNode = this.audioCtx.createGain();
    this.gainNode.gain.value = 0; // start silent
    this.rampTime = rampTime;
    this.gainNode.connect(this.audioCtx.destination);
  }

  async load(url: string) {
    const res = await fetch(url);
    const arrayBuf = await res.arrayBuffer();
    this.buffer = await this.audioCtx.decodeAudioData(arrayBuf);
  }

  private startLoop() {
    if (!this.buffer) return;

    this.source = this.audioCtx.createBufferSource();
    this.source.buffer = this.buffer;
    this.source.loop = true;
    this.source.playbackRate.value = this.rate;
    this.source.connect(this.gainNode);
    this.source.start(0);
  }

  play() {
    if (this.isPlaying) return;

    this.startLoop();
    this.smoothSetVolume(this.targetVolume);
    this.isPlaying = true;
  }

  pause() {
    if (!this.isPlaying) return;

    this.smoothSetVolume(0, () => {
      if (this.source) this.source.stop();
      this.source = null;
      this.isPlaying = false;
    });
  }

  restart() {
    if (this.source) this.source.stop();
    this.source = null;
    this.startLoop();
    this.smoothSetVolume(this.targetVolume);
    this.isPlaying = true;
  }

  // ==========================================
  // EXPRESSIVE VOLUME
  // ==========================================
  setExpressiveVolume(gesture: number) {
    gesture = Math.min(1, Math.max(0, gesture));
    const multiplier = 0.5 + gesture; // 0.5–1.5
    let vol = multiplier * 0.7; // ~0.35–1.05
    vol = Math.min(1.0, Math.max(0.35, vol));
    this.setVolume(vol);
  }

  setVolume(vol: number) {
    this.targetVolume = Math.max(0, Math.min(1, vol));
    this.smoothSetVolume(this.targetVolume);
  }

  private smoothSetVolume(target: number, onFinish?: () => void) {
    const start = this.currentVolume;
    const end = target;
    const duration = this.rampTime;
    const startTime = performance.now();

    const step = () => {
      const t = (performance.now() - startTime) / (duration * 1000);

      if (t >= 1) {
        this.gainNode.gain.value = end;
        this.currentVolume = end;
        if (onFinish) onFinish();
        return;
      }

      const value = start + (end - start) * t;
      this.gainNode.gain.value = value;
      this.currentVolume = value;

      this.rafId = requestAnimationFrame(step);
    };

    if (this.rafId) cancelAnimationFrame(this.rafId);
    this.rafId = requestAnimationFrame(step);
  }

  // ==========================================
  // RATE CONTROL
  // ==========================================
  setRate(rate: number) {
    rate = Math.min(2.0, Math.max(0.5, rate));
    this.rate = rate;
    if (this.source) {
      this.source.playbackRate.value = rate;
    }
  }

  // ==========================================
  // STATUS
  // ==========================================
  getPlaying() {
    return this.isPlaying;
  }
}
