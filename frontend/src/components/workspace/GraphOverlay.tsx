import type { GraphData } from "../../types/atlas";
import { useGraphSelection } from "../../context/GraphSelectionContext";

interface GraphOverlayProps {
  graph: GraphData;
  imageWidth: number;
  imageHeight: number;
}

const GraphOverlay = ({
  graph,
  imageWidth,
  imageHeight,
}: GraphOverlayProps) => {
  const {
    selectedNodeId,
    setSelectedNodeId,
  } = useGraphSelection();

  return (
    <svg
      className="absolute inset-0 w-full h-full"
      viewBox={`0 0 ${imageWidth} ${imageHeight}`}
      preserveAspectRatio="xMidYMid meet"
    >
      {/* -------------------------------- */}
      {/* Actual topology road paths       */}
      {/* -------------------------------- */}

      {graph.edges.map((edge, index) => {
        if (
          !edge.pixels ||
          edge.pixels.length < 2
        ) {
          return null;
        }

        const points = edge.pixels
          .map(
            (point) =>
              `${point.x},${point.y}`
          )
          .join(" ");

        return (
          <polyline
            key={`edge-${index}`}
            points={points}
            fill="none"
            stroke="#00FFFF"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
            pointerEvents="none"
          />
        );
      })}

      {/* -------------------------------- */}
      {/* Topology nodes                   */}
      {/* -------------------------------- */}

      {graph.nodes.map((node) => (
        <circle
          key={node.id}
          cx={node.x}
          cy={node.y}
          r={
            selectedNodeId === node.id
              ? 5
              : 3
          }
          fill={
            selectedNodeId === node.id
              ? "#ffcc00"
              : "#ff4040"
          }
          stroke="white"
          strokeWidth={1}
          style={{
            cursor: "pointer",
          }}
          onClick={() =>
            setSelectedNodeId(node.id)
          }
        />
      ))}
    </svg>
  );
};

export default GraphOverlay;