import type { BeatDetectionConfig } from "../config/trackingConfig";

const MS_IN_SECOND = 1000;

export class BeatDetector {
  private filteredY: number | null = null;
  private lastDownbeatTimeMs: number | null = null;
  private emaBpm: number | null = null;
  private lastPeakY: number | null = null;
  private recovered = true;
  private config: BeatDetectionConfig;

  constructor(config: BeatDetectionConfig) {
    this.config = config;
  }

  updateConfig(config: BeatDetectionConfig) {
    this.config = config;
    this.filteredY = null;
    this.lastPeakY = null;
    this.recovered = true;
  }

  update(y: number | null, timestampMs: number): number | null {
    if (typeof y !== "number") {
      this.filteredY = null;
      this.lastPeakY = null;
      this.recovered = true;
      return this.emaBpm;
    }

    if (this.filteredY === null) {
      this.filteredY = y;
      this.lastPeakY = y;
      return this.emaBpm;
    }

    const previousFiltered = this.filteredY;
    this.filteredY =
      this.config.positionAlpha * y +
      (1 - this.config.positionAlpha) * previousFiltered;
    const velocity = this.filteredY - previousFiltered;

    if (velocity < this.config.reverseVelocityLimit) {
      return this.emaBpm;
    }

    if (!this.recovered && this.lastPeakY !== null) {
      const recoveredDistance = this.lastPeakY - this.filteredY;
      if (recoveredDistance >= this.config.minRecoveryPixels) {
        this.recovered = true;
      } else {
        return this.emaBpm;
      }
    }

    if (velocity > this.config.velocityThreshold) {
      if (
        this.lastPeakY !== null &&
        this.filteredY - this.lastPeakY < this.config.minStrokePixels
      ) {
        return this.emaBpm;
      }

      if (
        this.lastDownbeatTimeMs !== null &&
        timestampMs - this.lastDownbeatTimeMs < this.config.minIntervalMs
      ) {
        return this.emaBpm;
      }

      if (this.lastDownbeatTimeMs !== null) {
        const intervalSec =
          (timestampMs - this.lastDownbeatTimeMs) / MS_IN_SECOND;
        if (intervalSec > 0) {
          const bpm = this.clamp(60 / intervalSec, 40, 200);
          this.emaBpm =
            this.emaBpm === null ? bpm : 0.15 * bpm + 0.85 * this.emaBpm;
        }
      }

      this.lastPeakY = this.filteredY;
      this.lastDownbeatTimeMs = timestampMs;
      this.recovered = false;
    }

    return this.emaBpm;
  }

  private clamp(value: number, min: number, max: number) {
    return Math.max(min, Math.min(max, value));
  }
}
