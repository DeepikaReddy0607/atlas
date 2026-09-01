// ============================================================
// ATLAS API TYPES
// ============================================================

// -----------------------------
// Segmentation
// -----------------------------

export interface SegmentationMetadata {
  model_id: string;
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
  node: [number, number];
  score: number;
}

export interface EdgeCriticality {
  edge: [
    [number, number],
    [number, number]
  ];
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
  critical_node: [number, number];
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

  removed_nodes: [number, number][];

  removed_edges: [
    [number, number],
    [number, number]
  ][];

  original_nodes: number;
  original_edges: number;

  remaining_nodes: number;
  remaining_edges: number;

  connected_components: number;
  largest_component: number;

  critical_node: [number, number];
}


// -----------------------------
// Visualizations
// -----------------------------

export interface VisualizationResult {
  /**
   * Satellite image with segmentation overlay.
   *
   * Usually returned as a base64 string or
   * an already prepared data URL.
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

  simulation: SimulationResult;

  recommendation: string;

  visualizations: VisualizationResult;
}