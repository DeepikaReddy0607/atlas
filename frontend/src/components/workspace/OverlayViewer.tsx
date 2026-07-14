import { useState } from "react";
import ViewerToolbar from "./ViewerToolbar";

interface OverlayViewerProps {
  imageUrl: string;
  overlayUrl: string;
  opacity: number;
  showOverlay: boolean;
}

const OverlayViewer = ({
  imageUrl,
  overlayUrl,
  opacity,
  showOverlay,
}: OverlayViewerProps) => {
  const [scale, setScale] = useState(1);

  const [position, setPosition] = useState({
    x: 0,
    y: 0,
  });

  const [dragging, setDragging] = useState(false);

  const [lastMouse, setLastMouse] = useState({
    x: 0,
    y: 0,
  });

  const handleWheel = (
    e: React.WheelEvent<HTMLDivElement>
  ) => {
    e.preventDefault();

    const zoomSpeed = 0.1;

    const nextScale =
      e.deltaY < 0
        ? scale + zoomSpeed
        : scale - zoomSpeed;

    setScale(Math.min(Math.max(nextScale, 0.5), 8));
  };

  const handleMouseDown = (
    e: React.MouseEvent<HTMLDivElement>
  ) => {
    setDragging(true);

    setLastMouse({
      x: e.clientX,
      y: e.clientY,
    });
  };

  const handleMouseMove = (
    e: React.MouseEvent<HTMLDivElement>
  ) => {
    if (!dragging) return;

    const dx = e.clientX - lastMouse.x;
    const dy = e.clientY - lastMouse.y;

    setPosition((prev) => ({
      x: prev.x + dx,
      y: prev.y + dy,
    }));

    setLastMouse({
      x: e.clientX,
      y: e.clientY,
    });
  };

  const handleMouseUp = () => {
    setDragging(false);
  };

  const resetView = () => {
    setScale(1);

    setPosition({
      x: 0,
      y: 0,
    });
  };
  const zoomIn = () => {
  setScale((prev) => Math.min(prev + 0.1, 8));
};

    const zoomOut = () => {
    setScale((prev) => Math.max(prev - 0.1, 0.5));
    };

    const fitToScreen = () => {
    setScale(1);
    setPosition({
        x: 0,
        y: 0,
    });
};
  return (
    <div
      className="
        relative
        flex
        h-full
        items-center
        justify-center
        overflow-hidden
        bg-[var(--atlas-bg)]
        cursor-grab
      "
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onDoubleClick={resetView}
    >
      <div
        style={{
          transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
          transformOrigin: "center",
          transition: dragging ? "none" : "transform 0.05s ease-out",
        }}
      >
        {/* Original Image */}
        <img
          src={imageUrl}
          alt="Satellite"
          className="
            max-h-full
            max-w-full
            object-contain
            select-none
          "
          draggable={false}
        />

        {/* AI Overlay */}
        <ViewerToolbar
            scale={scale}
            onZoomIn={zoomIn}
            onZoomOut={zoomOut}
            onReset={resetView}
            onFit={fitToScreen}
        />
        {showOverlay && (
          <img
            src={overlayUrl}
            alt="Segmentation Overlay"
            className="
              absolute
              inset-0
              h-full
              w-full
              object-contain
              pointer-events-none
            "
            style={{
              opacity,
            }}
            draggable={false}
          />
        )}
      </div>
    </div>
  );
};

export default OverlayViewer;