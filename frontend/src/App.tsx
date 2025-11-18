import "./styles.css";
import { useRef, useState } from "react";
import { useHandTracking } from "./hooks/useHandTracking";
import { CameraFeed } from "./components/CameraFeed";
import { HandOverlay } from "./components/HandOverlay";
import { DebugOverlay } from "./components/DebugOverlay";
import { ConfigOverlay } from "./components/ConfigOverlay";
import { defaultTrackingConfig } from "./config/trackingConfig";

export default function App() {
  const [trackingConfig, setTrackingConfig] = useState(defaultTrackingConfig);
  const { videoRef, hands, diagnostics } = useHandTracking(trackingConfig);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  return (
    <>
      <CameraFeed videoRef={videoRef} canvasRef={canvasRef} />
      <HandOverlay hands={hands} canvasRef={canvasRef} videoRef={videoRef} />
      <DebugOverlay diagnostics={diagnostics} />
      <ConfigOverlay
        config={trackingConfig}
        onConfigChange={setTrackingConfig}
      />
    </>
  );
}
