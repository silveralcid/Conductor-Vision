export type BeatDetectionConfig = {
  minIntervalMs: number;
  velocityThreshold: number;
  reverseVelocityLimit: number;
  minStrokePixels: number;
  minRecoveryPixels: number;
  positionAlpha: number;
  bpmAverageWindow: number;
};

export type DistanceConfig = {
  minSeparation: number;
  maxSeparation: number;
  averageWindow: number;
};

export type TrackingConfig = {
  beat: BeatDetectionConfig;
  distance: DistanceConfig;
};

export const defaultTrackingConfig: TrackingConfig = {
  beat: {
    minIntervalMs: 360,
    velocityThreshold: 2,
    reverseVelocityLimit: -3.5,
    minStrokePixels: 14,
    minRecoveryPixels: 22,
    positionAlpha: 0.35,
    bpmAverageWindow: 4,
  },
  distance: {
    minSeparation: 40,
    maxSeparation: 600,
    averageWindow: 4,
  },
};
