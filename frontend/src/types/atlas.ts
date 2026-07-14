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
// Graph Statistics
// -----------------------------

export interface GraphStats {
  nodes: number;
  edges: number;
}

// -----------------------------
// Criticality
// -----------------------------

export interface NodeCriticality {
  node: number[];
  score: number;
}

export interface EdgeCriticality {
  edge: number[][];
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
  critical_node: number[];
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

  removed_nodes: number[][];

  removed_edges: number[][][];

  original_nodes: number;
  original_edges: number;

  remaining_nodes: number;
  remaining_edges: number;

  connected_components: number;
  largest_component: number;

  critical_node: number[];
}

// -----------------------------
// Visualizations
// -----------------------------

export interface VisualizationResult {
  segmentation_overlay: string | null;
  road_mask: string | null;
  skeleton: string | null;
  graph: string | null;
  criticality: string | null;
}

// -----------------------------
// Root Response
// -----------------------------

export interface AtlasResult {
  segmentation: SegmentationResult;

  pixel_graph: GraphStats;

  topology_graph: GraphStats;

  criticality: CriticalityResult;

  resilience: ResilienceResult;

  risk: RiskResult;

  simulation: SimulationResult;

  recommendation: string;

  visualizations: VisualizationResult;
}