import { useEffect } from "react";
import type { HandLandmarkerResult } from "@mediapipe/tasks-vision";

type Props = {
  hands: HandLandmarkerResult | null;
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  videoRef: React.RefObject<HTMLVideoElement | null>;
};

export function HandOverlay({ hands, canvasRef, videoRef }: Props) {
  useEffect(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video || !hands) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!hands.landmarks || hands.landmarks.length === 0) return;

    // ----------------------------
    // MIRROR CANVAS OVERLAY
    // ----------------------------
    ctx.save();
    ctx.scale(-1, 1); // Flip horizontally
    ctx.translate(-canvas.width, 0);

    // Draw each detected hand
    hands.landmarks.forEach((landmarks) => {
      drawHand(landmarks, ctx);
    });

    ctx.restore();
  }, [hands]);

  return null;
}

function drawHand(
  landmarks: { x: number; y: number; z: number }[],
  ctx: CanvasRenderingContext2D
) {
  const W = ctx.canvas.width;
  const H = ctx.canvas.height;

  const edges = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [0, 5],
    [5, 6],
    [6, 7],
    [7, 8],
    [5, 9],
    [9, 10],
    [10, 11],
    [11, 12],
    [9, 13],
    [13, 14],
    [14, 15],
    [15, 16],
    [13, 17],
    [17, 18],
    [18, 19],
    [19, 20],
  ];

  ctx.lineWidth = 3;
  ctx.strokeStyle = "rgba(255,255,255,0.7)";

  edges.forEach(([i, j]) => {
    const p = landmarks[i];
    const q = landmarks[j];

    ctx.beginPath();
    ctx.moveTo(p.x * W, p.y * H);
    ctx.lineTo(q.x * W, q.y * H);
    ctx.stroke();
  });

  landmarks.forEach((p) => {
    ctx.beginPath();
    ctx.arc(p.x * W, p.y * H, 6, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255,255,255,0.9)";
    ctx.fill();
  });
}
