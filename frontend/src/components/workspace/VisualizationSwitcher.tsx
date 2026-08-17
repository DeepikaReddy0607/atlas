import type { Layer } from "../../types/layer";

interface Props {
  layers: Layer[];
  onSelect: (id: string) => void;
}

const VisualizationSwitcher = ({
  layers,
  onSelect,
}: Props) => {
  return (
    <div
      className="
        absolute
        left-4
        top-4
        z-40
        rounded-xl
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
        p-3
        shadow-xl
      "
    >
      <h3 className="mb-3 text-sm font-semibold">
        Visualization
      </h3>

      <div className="space-y-2">
        {layers.map((layer) => (
          <button
            key={layer.id}
            onClick={() => onSelect(layer.id)}
            className={`
              block
              w-full
              rounded-md
              px-3
              py-2
              text-left
              transition

              ${
                layer.visible
                  ? "bg-blue-600 text-white"
                  : "hover:bg-[var(--atlas-bg)]"
              }
            `}
          >
            {layer.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default VisualizationSwitcher;