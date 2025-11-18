import "./styles.css";
import { useRef } from "react";
import { useHandTracking } from "./hooks/useHandTracking";
import { CameraFeed } from "./components/CameraFeed";
import { HandOverlay } from "./components/HandOverlay";
import { DebugOverlay } from "./components/DebugOverlay";

export default function App() {
  const { videoRef, hands, diagnostics } = useHandTracking();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  return (
    <>
      <CameraFeed videoRef={videoRef} canvasRef={canvasRef} />
      <HandOverlay hands={hands} canvasRef={canvasRef} videoRef={videoRef} />
      <DebugOverlay diagnostics={diagnostics} />
    </>
  );
}
