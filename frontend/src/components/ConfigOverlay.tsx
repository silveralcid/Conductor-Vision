import type { TrackingConfig } from "../config/trackingConfig";

type Props = {
  config: TrackingConfig;
  onConfigChange: (config: TrackingConfig) => void;
};

export function ConfigOverlay({ config, onConfigChange }: Props) {
  const { beat, distance } = config;

  const updateBeat = (partial: Partial<typeof beat>) => {
    onConfigChange({
      ...config,
      beat: { ...beat, ...partial },
    });
  };

  const updateDistance = (partial: Partial<typeof distance>) => {
    onConfigChange({
      ...config,
      distance: { ...distance, ...partial },
    });
  };

  const adjustWindow = (delta: number) => {
    const next = Math.max(1, beat.bpmAverageWindow + delta);
    updateBeat({ bpmAverageWindow: next });
  };

  const handleNumberInput = (
    key: keyof typeof beat,
    value: number,
    min: number
  ) => {
    if (!Number.isFinite(value)) return;
    updateBeat({ [key]: Math.max(min, value) } as Partial<typeof beat>);
  };

  return (
    <div className="config-overlay">
      <h3>Beat Detection Config</h3>

      <div className="config-section">
        <span className="config-label">Average Window (min 1)</span>
        <div className="config-control">
          <button onClick={() => adjustWindow(-1)}>-</button>
          <input
            type="number"
            value={beat.bpmAverageWindow}
            min={1}
            onChange={(e) =>
              handleNumberInput(
                "bpmAverageWindow",
                Number(e.target.value),
                1
              )
            }
          />
          <button onClick={() => adjustWindow(1)}>+</button>
        </div>
      </div>

      <div className="config-section">
        <span className="config-label">Min Interval (ms) [200+]</span>
        <input
          type="number"
          value={beat.minIntervalMs}
          min={200}
          onChange={(e) =>
            handleNumberInput("minIntervalMs", Number(e.target.value), 200)
          }
        />
      </div>

      <div className="config-section">
        <span className="config-label">Stroke Threshold (px) [≥4]</span>
        <input
          type="number"
          value={beat.minStrokePixels}
          min={4}
          onChange={(e) =>
            handleNumberInput("minStrokePixels", Number(e.target.value), 4)
          }
        />
      </div>

      <h3>Distance Config</h3>

      <div className="config-section">
        <span className="config-label">Min Distance (px)</span>
        <input
          type="number"
          value={distance.minSeparation}
          min={0}
          onChange={(e) => {
            const next = Math.max(0, Number(e.target.value));
            if (!Number.isFinite(next)) return;
            updateDistance({
              minSeparation: next,
              maxSeparation: Math.max(next + 1, distance.maxSeparation),
            });
          }}
        />
      </div>

      <div className="config-section">
        <span className="config-label">Max Distance (px)</span>
        <input
          type="number"
          value={distance.maxSeparation}
          min={distance.minSeparation + 1}
          onChange={(e) => {
            const next = Number(e.target.value);
            if (!Number.isFinite(next)) return;
            updateDistance({
              maxSeparation: Math.max(distance.minSeparation + 1, next),
            });
          }}
        />
      </div>

      <div className="config-section">
        <span className="config-label">Distance Avg Window (min 1)</span>
        <div className="config-control">
          <button
            onClick={() =>
              updateDistance({
                averageWindow: Math.max(1, distance.averageWindow - 1),
              })
            }
          >
            -
          </button>
          <input
            type="number"
            value={distance.averageWindow}
            min={1}
            onChange={(e) => {
              const parsed = Number(e.target.value);
              if (!Number.isFinite(parsed)) return;
              const next = Math.max(1, parsed);
              updateDistance({ averageWindow: next });
            }}
          />
          <button
            onClick={() =>
              updateDistance({ averageWindow: distance.averageWindow + 1 })
            }
          >
            +
          </button>
        </div>
      </div>
    </div>
  );
}
