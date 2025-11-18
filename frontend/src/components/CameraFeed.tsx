type Props = {
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  videoRef: React.RefObject<HTMLVideoElement | null>;
};

export function CameraFeed({ canvasRef, videoRef }: Props) {
  return (
    <div className="app-root">
      <video ref={videoRef} className="webcam-feed" autoPlay playsInline />
      <canvas ref={canvasRef} className="output-canvas" />
    </div>
  );
}
