import type {
  GraphData,
  SimulationResult,
} from "../../types/atlas";

interface SimulationImpactOverlayProps {
  result: SimulationResult;
  graph?: GraphData;
  imageWidth: number;
  imageHeight: number;
  opacity?: number;
}

interface Component {
  id: number;
  nodeIds: number[];
  edgeIds: number[];
}

const COMPONENT_COLORS = [
  "#22c55e",
  "#38bdf8",
  "#a78bfa",
  "#f59e0b",
  "#f472b6",
  "#14b8a6",
  "#fb7185",
  "#818cf8",
];

const SimulationImpactOverlay = ({
  result,
  graph,
  imageWidth,
  imageHeight,
  opacity = 1,
}: SimulationImpactOverlayProps) => {
  /*
   * ---------------------------------------------------------
   * No graph available
   * ---------------------------------------------------------
   */

  if (!graph) {
    return (
      <svg
        className="absolute inset-0 h-full w-full pointer-events-none"
        viewBox={`0 0 ${imageWidth} ${imageHeight}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ opacity }}
      >
        <FailedNodes result={result} />
      </svg>
    );
  }

  /*
   * ---------------------------------------------------------
   * Determine failed nodes
   *
   * Backend coordinates:
   * [row, column]
   *
   * GraphData:
   * x = column
   * y = row
   * ---------------------------------------------------------
   */

  const removedNodeIds = new Set<number>();

  for (const removedNode of result.removed_nodes) {
    const nodeId = findNodeId(
      graph,
      removedNode
    );

    if (nodeId !== null) {
      removedNodeIds.add(nodeId);
    }
  }

  /*
   * ---------------------------------------------------------
   * Determine removed edges
   * ---------------------------------------------------------
   */

  const removedEdgeIds = new Set<number>();

  graph.edges.forEach((edge, index) => {
    const source = graph.nodes.find(
      (node) => node.id === edge.source
    );

    const target = graph.nodes.find(
      (node) => node.id === edge.target
    );

    if (!source || !target) {
      return;
    }

    const removed =
      result.removed_edges.some(
        ([start, end]) =>
          graphCoordinateMatches(
            source,
            start
          ) &&
          graphCoordinateMatches(
            target,
            end
          )
      );

    const removedReverse =
      result.removed_edges.some(
        ([start, end]) =>
          graphCoordinateMatches(
            source,
            end
          ) &&
          graphCoordinateMatches(
            target,
            start
          )
      );

    if (
      removed ||
      removedReverse
    ) {
      removedEdgeIds.add(index);
    }
  });

  /*
   * ---------------------------------------------------------
   * Build surviving graph
   * ---------------------------------------------------------
   */

  const survivingNodes =
    graph.nodes.filter(
      (node) =>
        !removedNodeIds.has(node.id)
    );

  const survivingEdges =
    graph.edges.filter(
      (_, index) =>
        !removedEdgeIds.has(index)
    );

  /*
   * Remove edges connected to failed nodes.
   *
   * A failed node is no longer part of
   * the simulated network.
   */

  const validEdges =
    survivingEdges.filter(
      (edge) =>
        !removedNodeIds.has(
          edge.source
        ) &&
        !removedNodeIds.has(
          edge.target
        )
    );

  /*
   * ---------------------------------------------------------
   * Calculate connected components
   * ---------------------------------------------------------
   */

  const components =
    calculateComponents(
      survivingNodes,
      validEdges
    );

  /*
   * ---------------------------------------------------------
   * Node → component lookup
   * ---------------------------------------------------------
   */

  const nodeComponentMap =
    new Map<number, number>();

  components.forEach(
    (component) => {
      component.nodeIds.forEach(
        (nodeId) => {
          nodeComponentMap.set(
            nodeId,
            component.id
          );
        }
      );
    }
  );

  return (
    <svg
      className="
        absolute
        inset-0
        h-full
        w-full
        pointer-events-none
      "
      viewBox={`0 0 ${imageWidth} ${imageHeight}`}
      preserveAspectRatio="xMidYMid meet"
      style={{ opacity }}
    >
      {/* ===================================================
          SURVIVING EDGES
      ==================================================== */}

      {validEdges.map(
        (edge, index) => {
          const source =
            graph.nodes.find(
              (node) =>
                node.id === edge.source
            );

          const target =
            graph.nodes.find(
              (node) =>
                node.id === edge.target
            );

          if (
            !source ||
            !target
          ) {
            return null;
          }

          const componentId =
            nodeComponentMap.get(
              source.id
            );

          const stroke =
            componentId !== undefined
              ? COMPONENT_COLORS[
                  componentId %
                    COMPONENT_COLORS.length
                ]
              : "#94a3b8";

          return (
            <line
              key={`component-edge-${index}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke={stroke}
              strokeWidth="2.5"
              strokeLinecap="round"
              opacity="0.8"
            />
          );
        }
      )}

      {/* ===================================================
          SURVIVING NODES
      ==================================================== */}

      {survivingNodes.map(
        (node) => {
          const componentId =
            nodeComponentMap.get(
              node.id
            );

          const fill =
            componentId !== undefined
              ? COMPONENT_COLORS[
                  componentId %
                    COMPONENT_COLORS.length
                ]
              : "#94a3b8";

          return (
            <circle
              key={`component-node-${node.id}`}
              cx={node.x}
              cy={node.y}
              r="3.5"
              fill={fill}
              stroke="#ffffff"
              strokeWidth="1"
              opacity="0.9"
            />
          );
        }
      )}

      {/* ===================================================
          REMOVED EDGES
      ==================================================== */}

      {graph.edges.map(
        (edge, index) => {
          if (
            !removedEdgeIds.has(
              index
            )
          ) {
            return null;
          }

          const source =
            graph.nodes.find(
              (node) =>
                node.id === edge.source
            );

          const target =
            graph.nodes.find(
              (node) =>
                node.id === edge.target
            );

          if (
            !source ||
            !target
          ) {
            return null;
          }

          return (
            <line
              key={`removed-edge-${index}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="#ef4444"
              strokeWidth="4"
              strokeLinecap="round"
              opacity="0.95"
            />
          );
        }
      )}

      {/* ===================================================
          FAILED NODES
      ==================================================== */}

      <FailedNodes
        result={result}
      />

      {/* ===================================================
          COMPONENT COUNT
      ==================================================== */}

      {components.length > 0 && (
        <g>
          <rect
            x="10"
            y="10"
            width="170"
            height="34"
            rx="6"
            fill="rgba(15, 23, 42, 0.85)"
          />

          <text
            x="22"
            y="32"
            fill="#ffffff"
            fontSize="14"
            fontWeight="600"
          >
            {components.length} components
          </text>
        </g>
      )}
    </svg>
  );
};

/* ============================================================
   Failed Nodes
============================================================ */

interface FailedNodesProps {
  result: SimulationResult;
}

const FailedNodes = ({
  result,
}: FailedNodesProps) => {
  return (
    <>
      {result.removed_nodes.map(
        (node, index) => {
          /*
           * Backend:
           * [row, column]
           *
           * SVG:
           * x = column
           * y = row
           */

          const [row, column] =
            node;

          const x = column;
          const y = row;

          return (
            <g
              key={`failed-node-${index}`}
            >
              {/* Impact ring */}

              <circle
                cx={x}
                cy={y}
                r="15"
                fill="none"
                stroke="#ef4444"
                strokeWidth="2"
                opacity="0.35"
              />

              {/* Failed node */}

              <circle
                cx={x}
                cy={y}
                r="8"
                fill="#ef4444"
                stroke="#ffffff"
                strokeWidth="2"
              />

              {/* Center */}

              <circle
                cx={x}
                cy={y}
                r="3"
                fill="#ffffff"
              />
            </g>
          );
        }
      )}
    </>
  );
};

/* ============================================================
   Connected Components
============================================================ */

const calculateComponents = (
  nodes: GraphData["nodes"],
  edges: GraphData["edges"]
): Component[] => {
  /*
   * Build adjacency list
   */

  const adjacency =
    new Map<number, number[]>();

  nodes.forEach((node) => {
    adjacency.set(
      node.id,
      []
    );
  });

  edges.forEach((edge) => {
    const sourceNeighbors =
      adjacency.get(
        edge.source
      );

    const targetNeighbors =
      adjacency.get(
        edge.target
      );

    if (sourceNeighbors) {
      sourceNeighbors.push(
        edge.target
      );
    }

    if (targetNeighbors) {
      targetNeighbors.push(
        edge.source
      );
    }
  });

  /*
   * BFS
   */

  const visited =
    new Set<number>();

  const components: Component[] =
    [];

  let componentId = 0;

  for (const node of nodes) {
    if (
      visited.has(node.id)
    ) {
      continue;
    }

    const queue: number[] = [
      node.id,
    ];

    const nodeIds: number[] =
      [];

    visited.add(node.id);

    while (
      queue.length > 0
    ) {
      const current =
        queue.shift();

      if (
        current === undefined
      ) {
        continue;
      }

      nodeIds.push(
        current
      );

      const neighbors =
        adjacency.get(
          current
        ) ?? [];

      for (
        const neighbor of neighbors
      ) {
        if (
          visited.has(
            neighbor
          )
        ) {
          continue;
        }

        visited.add(
          neighbor
        );

        queue.push(
          neighbor
        );
      }
    }

    /*
     * Find edges belonging
     * to this component.
     */

    const nodeSet =
      new Set(nodeIds);

    const edgeIds: number[] =
      [];

    edges.forEach(
      (edge, index) => {
        if (
          nodeSet.has(
            edge.source
          ) &&
          nodeSet.has(
            edge.target
          )
        ) {
          edgeIds.push(
            index
          );
        }
      }
    );

    components.push({
      id: componentId,
      nodeIds,
      edgeIds,
    });

    componentId++;
  }

  /*
   * Largest component first.
   */

  components.sort(
    (a, b) =>
      b.nodeIds.length -
      a.nodeIds.length
  );

  /*
   * Reassign IDs after sorting.
   */

  return components.map(
    (component, index) => ({
      ...component,
      id: index,
    })
  );
};

/* ============================================================
   Find Node
============================================================ */

const findNodeId = (
  graph: GraphData,
  coordinate: [number, number]
): number | null => {
  /*
   * Backend:
   * [row, column]
   *
   * GraphData:
   * x = column
   * y = row
   */

  const [row, column] =
    coordinate;

  const node =
    graph.nodes.find(
      (candidate) =>
        candidate.x === column &&
        candidate.y === row
    );

  return node?.id ?? null;
};

/* ============================================================
   Match Graph Coordinate
============================================================ */

const graphCoordinateMatches = (
  node: GraphData["nodes"][number],
  coordinate: [number, number]
) => {
  /*
   * Backend:
   * [row, column]
   */

  const [row, column] =
    coordinate;

  /*
   * GraphData:
   * x = column
   * y = row
   */

  return (
    node.x === column &&
    node.y === row
  );
};

export default SimulationImpactOverlay;