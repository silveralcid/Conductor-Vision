import { useState, useEffect, useRef } from "react";
import {
  FilesetResolver,
  HandLandmarker,
  type HandLandmarkerResult,
} from "@mediapipe/tasks-vision";
import { BeatDetector } from "../utils/beatDetector";
import type { TrackingConfig } from "../config/trackingConfig";

type HandPoint = { x: number; y: number } | null;
const PALM_INDICES = [0, 5, 9, 13, 17];

export type TrackingDiagnostics = {
  fps: number;
  buffer: number;
  leftHand: HandPoint;
  rightHand: HandPoint;
  recorderActive: boolean;
  bpm: number | null;
  volume: number | null;
  musicStatus: "IDLE" | "PLAYING" | "PAUSED";
  playbackRate: number;
  volumeEnabled: boolean;
  tempoEnabled: boolean;
  autoPaused: boolean;
};

export function useHandTracking(config: TrackingConfig) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const detector = useRef<HandLandmarker | null>(null);

  const [hands, setHands] = useState<HandLandmarkerResult | null>(null);
  const [diagnostics, setDiagnostics] = useState<TrackingDiagnostics>({
    fps: 0,
    buffer: 0,
    leftHand: null,
    rightHand: null,
    recorderActive: false,
    bpm: null,
    volume: null,
    musicStatus: "IDLE",
    playbackRate: 1,
    volumeEnabled: false,
    tempoEnabled: false,
    autoPaused: false,
  });

  const lastFrameTime = useRef(performance.now());
  const beatDetectorRef = useRef(new BeatDetector(config.beat));
  const bpmSamplesRef = useRef<number[]>([]);

  useEffect(() => {
    beatDetectorRef.current.updateConfig(config.beat);
    bpmSamplesRef.current = [];
  }, [config.beat]);

  // Webcam
  useEffect(() => {
    (async () => {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1920, height: 1080 },
      });

      if (videoRef.current) videoRef.current.srcObject = stream;
    })();
  }, []);

  // Load MediaPipe
  useEffect(() => {
    let mounted = true;

    (async () => {
      const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22-rc.20250304/wasm"
      );

      if (!mounted) return;

      detector.current = await HandLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        },
        runningMode: "VIDEO",
        numHands: 2,
      });
    })();

    return () => {
      mounted = false;
    };
  }, []);

  // Main loop
  useEffect(() => {
    let frameId: number;

    const loop = () => {
      const video = videoRef.current;
      const lm = detector.current;

      if (!video || !lm || video.readyState !== 4) {
        frameId = requestAnimationFrame(loop);
        return;
      }

      const now = performance.now();
      const results = lm.detectForVideo(video, now);
      setHands(results);

      const buffer = results.landmarks?.length ?? 0;
      let left: HandPoint = null;
      let right: HandPoint = null;
      let rightBeatY: number | null = null;

      if (results.landmarks && video.videoWidth && video.videoHeight) {
        results.landmarks.forEach((landmarks, index) => {
          const wrist = landmarks[0];
          const handedness =
            results.handedness?.[index]?.[0]?.categoryName ?? "";
          const handednessUpper = handedness.toUpperCase();

          const coords = {
            x: Math.round(wrist.x * video.videoWidth),
            y: Math.round(wrist.y * video.videoHeight),
          };

          const centroidNormalized =
            PALM_INDICES.reduce((sum, idx) => sum + landmarks[idx].y, 0) /
            PALM_INDICES.length;
          const centroidYPixels = Math.round(
            centroidNormalized * video.videoHeight
          );
          const setRight = () => {
            right = coords;
            rightBeatY = centroidYPixels;
          };

          if (handednessUpper === "LEFT") {
            left = coords;
          } else if (handednessUpper === "RIGHT") {
            setRight();
          } else if (!left) {
            left = coords;
          } else if (!right) {
            setRight();
          }
        });
      }

      if (right && rightBeatY === null) {
        rightBeatY = right.y;
      }

      const deltaMs = now - lastFrameTime.current;
      lastFrameTime.current = now;
      const fpsValue = deltaMs > 0 ? Math.round((1000 / deltaMs) * 10) / 10 : 0;
      const bpm = beatDetectorRef.current.update(rightBeatY, now);
      const windowSize = Math.max(1, Math.floor(config.beat.bpmAverageWindow));
      if (bpm !== null) {
        const samples = bpmSamplesRef.current;
        samples.push(bpm);
        while (samples.length > windowSize) samples.shift();
      }

      const averagedBpm =
        bpmSamplesRef.current.length > 0
          ? bpmSamplesRef.current.reduce((sum, value) => sum + value, 0) /
            bpmSamplesRef.current.length
          : bpm;
      const roundedBpm =
        averagedBpm !== null && averagedBpm !== undefined
          ? Math.round(averagedBpm * 10) / 10
          : averagedBpm;

      setDiagnostics((prev) => ({
        ...prev,
        fps: fpsValue || prev.fps,
        buffer,
        leftHand: left,
        rightHand: right,
        bpm: roundedBpm ?? prev.bpm,
      }));

      frameId = requestAnimationFrame(loop);
    };

    frameId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frameId);
  }, []);

  return { videoRef, hands, diagnostics };
}
