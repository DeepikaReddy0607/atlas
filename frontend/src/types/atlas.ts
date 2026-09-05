// ============================================================
// ATLAS API TYPES
// ============================================================

// -----------------------------
// Shared coordinate types
// -----------------------------

export type Coordinate = [number, number];

export type EdgeCoordinate = [
  Coordinate,
  Coordinate
];


// -----------------------------
// Segmentation
// -----------------------------

export interface SegmentationMetadata {
  [key: string]: unknown;
}

export interface SegmentationResult {
  model_name: string;
  inference_time_ms: number;
  image_size: number[];
  mask_shape: number[];
  metadata: SegmentationMetadata;
}


// -----------------------------
// Graph
// -----------------------------

export interface GraphNode {
  id: number;
  x: number;
  y: number;
}

export interface GraphPoint {
  x: number;
  y: number;
}

export interface GraphEdge {
  source: number;
  target: number;
  pixels: GraphPoint[];
  length: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphStats {
  nodes: number;
  edges: number;
}


// -----------------------------
// Criticality
// -----------------------------

export interface NodeCriticality {
  node: Coordinate;
  score: number;
}

export interface EdgeCriticality {
  edge: EdgeCoordinate;
  score: number;
}

export interface CriticalityResult {
  node: NodeCriticality[];
  edge: EdgeCriticality[];
}


// -----------------------------
// Resilience
// -----------------------------

export interface ResilienceResult {
  critical_node: Coordinate | null;
  connected_components: number;
  largest_component: number;
}


// -----------------------------
// Risk
// -----------------------------

export interface RiskResult {
  ari: number;
  level: string;
  recommendation: string;
}


// -----------------------------
// Simulation
// -----------------------------

export interface SimulationResult {
  scenario: string;

  removed_nodes: Coordinate[];

  removed_edges: EdgeCoordinate[];

  original_nodes: number;
  original_edges: number;

  remaining_nodes: number;
  remaining_edges: number;

  connected_components: number;
  largest_component: number;

  critical_node: Coordinate | null;
}


// -----------------------------
// Visualizations
// -----------------------------

export interface VisualizationResult {
  /**
   * Satellite image with segmentation overlay.
   */
  segmentation_overlay: string | null;

  /**
   * Extracted road mask visualization.
   */
  road_mask: string | null;

  /**
   * Skeletonized road network.
   */
  skeleton: string | null;

  /**
   * Topological graph visualization.
   */
  graph: string | null;

  /**
   * Criticality visualization.
   */
  criticality: string | null;
}


// -----------------------------
// Root Response
// -----------------------------

export interface AtlasResult {
  segmentation: SegmentationResult;

  pixel_graph: GraphStats;

  topology_graph: GraphStats;

  topology_graph_data: GraphData;

  criticality: CriticalityResult;

  resilience: ResilienceResult;

  risk: RiskResult;

  simulation: SimulationResult | null;

  recommendation: string | null;

  visualizations: VisualizationResult;
}