import type { TrackingDiagnostics } from "../hooks/useHandTracking";

type Props = {
  diagnostics: TrackingDiagnostics;
};

const formatCoord = (point: { x: number; y: number } | null) =>
  point ? `${point.x}px, ${point.y}px` : "--";

const formatNullable = (value: number | null, digits = 1) =>
  value === null ? "--" : value.toFixed(digits);

export function DebugOverlay({ diagnostics }: Props) {
  const {
    fps,
    buffer,
    leftHand,
    rightHand,
    recorderActive,
    bpm,
    volume,
    musicStatus,
    playbackRate,
    volumeEnabled,
    tempoEnabled,
    autoPaused,
  } = diagnostics;

  return (
    <div className="debug-overlay">
      <div className="hud-row">
        <span className="hud-label">FPS</span>
        <span className="hud-value">{fps.toFixed(1)}</span>
      </div>
      <div className="hud-row">
        <span className="hud-label">BUFFER</span>
        <span className="hud-value">{buffer}</span>
      </div>
      <div className="hud-row">
        <span className="hud-label">LEFT</span>
        <span className="hud-value">{formatCoord(leftHand)}</span>
      </div>
      <div className="hud-row">
        <span className="hud-label">RIGHT</span>
        <span className="hud-value">{formatCoord(rightHand)}</span>
      </div>

      <div className="hud-divider" />

      <div className="hud-row status-row">
        <span className="hud-label">REC</span>
        <span
          className={`hud-pill ${recorderActive ? "live" : "idle"}`}
        >
          {recorderActive ? "LIVE" : "STANDBY"}
        </span>
      </div>

      <div className="hud-row">
        <span className="hud-label">BPM</span>
        <span className="hud-value">{formatNullable(bpm)}</span>
      </div>
      <div className="hud-row">
        <span className="hud-label">VOL</span>
        <span className="hud-value">{formatNullable(volume, 2)}</span>
      </div>

      <div className="hud-row">
        <span className="hud-label">MUSIC</span>
        <span className="hud-value">{musicStatus}</span>
      </div>
      <div className="hud-row">
        <span className="hud-label">RATE</span>
        <span className="hud-value">{playbackRate.toFixed(2)}x</span>
      </div>

      <div className="hud-divider" />

      <div className="hud-toggles">
        <span className={`hud-pill ${volumeEnabled ? "on" : "off"}`}>
          VOLCTL {volumeEnabled ? "ON" : "OFF"}
        </span>
        <span className={`hud-pill ${tempoEnabled ? "on" : "off"}`}>
          TEMPOCTL {tempoEnabled ? "ON" : "OFF"}
        </span>
      </div>

      <div className="hud-status">
        <span className={`hud-pill ${autoPaused ? "warning" : "success"}`}>
          {autoPaused ? "AUTO-PAUSED" : "ACTIVE"}
        </span>
      </div>
    </div>
  );
}
