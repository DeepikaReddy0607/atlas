import type { Layer } from "../../types/layer";

interface LayerPanelProps {
  layers: Layer[];
  onToggle: (id: string) => void;
  onOpacityChange: (id: string, opacity: number) => void;
}

const LayerPanel = ({
  layers,
  onToggle,
  onOpacityChange,
}: LayerPanelProps) => {
  return (
    <div
      className="
        absolute
        top-4
        right-4
        w-72
        rounded-xl
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
        p-4
        shadow-xl
        z-40
      "
    >
      <h2 className="mb-4 text-lg font-semibold">
        Layers
      </h2>

      {layers.map((layer) => (
        <div
          key={layer.id}
          className="mb-4 rounded-lg border border-[var(--atlas-border)] p-3"
        >
          <label className="flex items-center justify-between">
            <span>{layer.name}</span>

            <input
              type="checkbox"
              checked={layer.visible}
              onChange={() => onToggle(layer.id)}
            />
          </label>

          <div className="mt-3">
            <label className="mb-1 block text-sm">
              Opacity
            </label>

            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={layer.opacity}
              onChange={(e) =>
                onOpacityChange(
                  layer.id,
                  Number(e.target.value)
                )
              }
              className="w-full"
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default LayerPanel;