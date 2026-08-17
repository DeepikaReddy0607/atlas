import {
  Layers,
  RotateCcw,
} from "lucide-react";

import { useLayers } from "../../context/LayerContext";
import { useLayerSelection } from "../../context/LayerSelectionContext";

const MapLayersPanel = () => {
  const {
    layers,
    toggleLayer,
    updateOpacity,
    resetLayers,
  } = useLayers();

  const {
    selectedLayerId,
    setSelectedLayerId,
  } = useLayerSelection();

  if (layers.length === 0) {
    return (
      <div className="p-6 text-center">
        <Layers
          size={42}
          className="
            mx-auto
            mb-4
            text-[var(--atlas-text-muted)]
            opacity-50
          "
        />

        <h2 className="text-lg font-semibold">
          No Layers Available
        </h2>

        <p className="mt-2 text-sm text-[var(--atlas-text-muted)]">
          Run an analysis to generate map layers.
        </p>
      </div>
    );
  }

  const activeLayer =
    layers.find(
      (layer) =>
        layer.id === selectedLayerId
    );

  return (
    <div
      className="
        h-full
        min-h-0
        overflow-y-auto
        p-5
      "
    >
      {/* Header */}

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Layers size={19} />

            <h2 className="text-xl font-semibold">
              Map & Layers
            </h2>
          </div>

          <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
            Manage visualization layers
          </p>
        </div>

        <button
          type="button"
          onClick={resetLayers}
          title="Reset layers"
          className="
            rounded-lg
            border
            border-[var(--atlas-border)]
            p-2
            text-[var(--atlas-text-muted)]
            transition
            hover:bg-[var(--atlas-bg)]
            hover:text-[var(--atlas-text)]
          "
        >
          <RotateCcw size={16} />
        </button>
      </div>

      {/* Layer list */}

      <div className="mt-6 space-y-3">
        {layers.map((layer) => {
          const selected =
            selectedLayerId ===
            layer.id;

          return (
            <div
              key={layer.id}
              onClick={() =>
                setSelectedLayerId(
                  layer.id
                )
              }
              className={`
                cursor-pointer
                rounded-xl
                border
                p-4
                transition-all

                ${
                  selected
                    ? "border-blue-500 bg-blue-500/10"
                    : "border-[var(--atlas-border)] bg-[var(--atlas-bg)]"
                }
              `}
            >
              {/* Layer header */}

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">
                    {layer.name}
                  </h3>

                  <p className="mt-0.5 text-xs uppercase tracking-wide text-[var(--atlas-text-muted)]">
                    {layer.type}
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={layer.visible}
                  onClick={(event) =>
                    event.stopPropagation()
                  }
                  onChange={() =>
                    toggleLayer(
                      layer.id
                    )
                  }
                />
              </div>

              {/* Opacity */}

              {layer.type !==
                "base" && (
                <div className="mt-4">
                  <div className="mb-2 flex justify-between text-xs">
                    <span>
                      Opacity
                    </span>

                    <span className="text-[var(--atlas-text-muted)]">
                      {Math.round(
                        layer.opacity *
                          100
                      )}
                      %
                    </span>
                  </div>

                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.05}
                    value={
                      layer.opacity
                    }
                    onClick={(event) =>
                      event.stopPropagation()
                    }
                    onChange={(event) =>
                      updateOpacity(
                        layer.id,
                        Number(
                          event.target
                            .value
                        )
                      )
                    }
                    className="w-full"
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Active layer */}

      {activeLayer && (
        <div
          className="
            mt-6
            rounded-xl
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-4
          "
        >
          <p className="text-xs uppercase tracking-wide text-[var(--atlas-text-muted)]">
            Active Layer
          </p>

          <p className="mt-1 font-semibold">
            {activeLayer.name}
          </p>

          <p className="mt-1 text-xs text-[var(--atlas-text-muted)]">
            {activeLayer.type}
          </p>
        </div>
      )}
    </div>
  );
};

export default MapLayersPanel;