interface ViewerToolbarProps {
  scale: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
  onFit: () => void;
}

const ViewerToolbar = ({
  scale,
  onZoomIn,
  onZoomOut,
  onReset,
  onFit,
}: ViewerToolbarProps) => {
  return (
    <div
      className="
        absolute
        top-4
        left-1/2
        -translate-x-1/2
        z-30
        flex
        items-center
        gap-2
        rounded-xl
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
        p-2
        shadow-xl
      "
    >
      <button onClick={onZoomIn}>+</button>

      <button onClick={onZoomOut}>−</button>

      <button onClick={onFit}>Fit</button>

      <button onClick={onReset}>Reset</button>

      <span className="ml-2 text-sm">
        {(scale * 100).toFixed(0)}%
      </span>
    </div>
  );
};

export default ViewerToolbar;