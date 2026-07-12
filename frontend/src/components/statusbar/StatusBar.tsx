const StatusBar = () => {
  return (
    <footer
      className="
        flex
        h-[var(--status-height)]
        items-center
        justify-between
        border-t
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
        px-4
        text-xs
        text-[var(--atlas-text-muted)]
      "
    >
      {/* Left */}
      <div className="flex items-center gap-5">

        <span>Ready</span>

        <span>Project: Untitled</span>

      </div>

      {/* Center */}
      <div className="flex items-center gap-5">

        <span>Zoom 100%</span>

        <span>Coordinates -- , --</span>

      </div>

      {/* Right */}
      <div className="flex items-center gap-5">

        <span>Model: ADE20K</span>

        <span>GPU: Idle</span>

      </div>

    </footer>
  );
};

export default StatusBar;