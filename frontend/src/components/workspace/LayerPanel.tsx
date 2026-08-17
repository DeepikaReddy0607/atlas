import { useLayers } from "../../context/LayerContext";
import { useLayerSelection } from "../../context/LayerSelectionContext";

const LayerPanel = () => {
  const {
    layers,
    toggleLayer,
    updateOpacity,
  } = useLayers();

  const {
    selectedLayerId,
    setSelectedLayerId,
  } = useLayerSelection();

  return (
    <div
      className="
        absolute
        top-4
        right-4
        z-40
        w-80
        rounded-xl
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
        shadow-2xl
      "
    >
      {/* Header */}

      <div
        className="
          border-b
          border-[var(--atlas-border)]
          px-5
          py-4
        "
      >
        <h2 className="text-lg font-semibold">
          Layer Manager
        </h2>

        <p className="text-sm text-[var(--atlas-text-muted)]">
          Toggle visualization layers
        </p>
      </div>

      {/* Layers */}

      <div
        className="
          max-h-[550px]
          space-y-4
          overflow-y-auto
          p-4
        "
      >
        {layers.map((layer) => (
          <div
            key={layer.id}
            onClick={() =>
              setSelectedLayerId(
                layer.id
              )
            }
            className={`
              cursor-pointer
              rounded-lg
              border
              p-3
              transition-all

              ${
                selectedLayerId === layer.id
                  ? "border-blue-500 bg-blue-500/10"
                  : "border-[var(--atlas-border)] bg-[var(--atlas-bg)]"
              }
            `}
          >
            {/* Layer Header */}

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">
                  {layer.name}
                </h3>

                <span
                  className="
                    text-xs
                    uppercase
                    tracking-wide
                    text-[var(--atlas-text-muted)]
                  "
                >
                  {layer.type}
                </span>
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

            {layer.type !== "base" && (
              <div className="mt-4">
                <div className="mb-2 flex justify-between text-sm">
                  <span>
                    Opacity
                  </span>

                  <span>
                    {Math.round(
                      layer.opacity * 100
                    )}
                    %
                  </span>
                </div>

                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={layer.opacity}
                  onClick={(event) =>
                    event.stopPropagation()
                  }
                  onChange={(event) =>
                    updateOpacity(
                      layer.id,
                      Number(
                        event.target.value
                      )
                    )
                  }
                  className="w-full"
                />
              </div>
            )}
          </div>
        ))}

        {/* Empty state */}

        {layers.length === 0 && (
          <div
            className="
              py-8
              text-center
              text-sm
              text-[var(--atlas-text-muted)]
            "
          >
            No visualization layers available.
          </div>
        )}
      </div>
    </div>
  );
};

export default LayerPanel;