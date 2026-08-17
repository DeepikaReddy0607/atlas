import { useState } from "react";

import type { Layer } from "../../types/layer";
import type { GraphData } from "../../types/atlas";

import ViewerToolbar from "./ViewerToolbar";
import GraphOverlay from "./GraphOverlay";

import { useSimulation } from "../../context/SimulationContext";
import SimulationImpactOverlay from "../viewer/SimulationImpactOverlay";

import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
interface OverlayViewerProps {
  imageUrl: string;
  layers: Layer[];
  graph?: GraphData;
}

const OverlayViewer = ({
  imageUrl,
  layers,
  graph,
}: OverlayViewerProps) => {
    const { analysisResult } = useAtlasAnalysis();
    const { result: simulationResult } = useSimulation();

    const imageWidth =
    analysisResult?.segmentation.image_size?.[0] ?? 512;

  const imageHeight =
    analysisResult?.segmentation.image_size?.[1] ?? 512;
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

    setScale(
      Math.min(
        Math.max(nextScale, 0.5),
        8
      )
    );
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
    setScale((prev) =>
      Math.min(prev + 0.1, 8)
    );
  };

  const zoomOut = () => {
    setScale((prev) =>
      Math.max(prev - 0.1, 0.5)
    );
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
        className="relative"
        style={{
          transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
          transformOrigin: "center",
          transition: dragging
            ? "none"
            : "transform 0.05s ease-out",
        }}
      >
        {/* Base Image */}
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

        {/* Raster Layers */}
        {layers
          .filter(
            (layer) =>
              layer.id !== "satellite" &&
              layer.id !== "graph" &&
              layer.visible &&
              layer.url
          )
          .map((layer) => (
            <img
              key={layer.id}
              src={layer.url}
              alt={layer.name}
              className="
                absolute
                inset-0
                h-full
                w-full
                object-contain
                pointer-events-none
              "
              style={{
                opacity: layer.opacity,
              }}
              draggable={false}
            />
          ))}

        {/* Interactive SVG Graph */}
        {graph &&
          layers.find(
            (l) =>
              l.id === "graph" &&
              l.visible
          ) && (
            <GraphOverlay
              graph={graph}
              imageWidth={imageWidth}
              imageHeight={imageHeight}
            />
          )}
          {/* Simulation Impact */}
          {simulationResult &&
            layers.find(
              (layer) =>
                layer.id === "simulation_impact" &&
                layer.visible
            ) && (
              <SimulationImpactOverlay
                result={simulationResult}
                graph={ graph }
                imageWidth={imageWidth}
                imageHeight={imageHeight}
                opacity={
                  layers.find(
                    (layer) =>
                      layer.id === "simulation_impact"
                  )?.opacity ?? 1
                }
              />
            )}
      </div>

      <ViewerToolbar
        scale={scale}
        onZoomIn={zoomIn}
        onZoomOut={zoomOut}
        onReset={resetView}
        onFit={fitToScreen}
      />
    </div>
  );
};

export default OverlayViewer;