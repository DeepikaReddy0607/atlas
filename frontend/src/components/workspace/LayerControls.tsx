interface LayerControlsProps {
  opacity: number;
  onOpacityChange: (opacity: number) => void;

  showOverlay: boolean;
  onToggleOverlay: () => void;
}

const LayerControls = ({
  opacity,
  onOpacityChange,
  showOverlay,
  onToggleOverlay,
}: LayerControlsProps) => {
  return (
    <div
      className="
        absolute
        top-6
        right-6
        z-20
        w-72
        rounded-xl
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
        shadow-2xl
        backdrop-blur-xl
      "
    >
      <div className="border-b border-[var(--atlas-border)] p-4">
        <h3 className="text-sm font-semibold">
          Layers
        </h3>
      </div>

      <div className="space-y-5 p-4">

        <div className="flex items-center justify-between">
          <span className="text-sm">
            Segmentation Overlay
          </span>

          <button
            onClick={onToggleOverlay}
            className="
              rounded-md
              border
              border-[var(--atlas-border)]
              px-3
              py-1
              text-xs
              transition
              hover:bg-white/5
            "
          >
            {showOverlay ? "Visible" : "Hidden"}
          </button>
        </div>

        <div>

          <label className="mb-2 block text-xs text-[var(--atlas-text-muted)]">
            Overlay Opacity
          </label>

          <input
            type="range"
            min={0}
            max={100}
            value={opacity * 100}
            onChange={(e) =>
              onOpacityChange(Number(e.target.value) / 100)
            }
            className="w-full"
          />

          <div className="mt-2 text-xs text-[var(--atlas-text-muted)]">
            {(opacity * 100).toFixed(0)}%
          </div>

        </div>

      </div>
    </div>
  );
};

export default LayerControls;