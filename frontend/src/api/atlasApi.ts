import api from "./axios";
import type {
  AtlasResult,
  SimulationResult,
} from "../types/atlas";


// ============================================================
// ANALYSIS
// ============================================================

export const analyzeImage = async (
  file: File
): Promise<AtlasResult> => {
  const formData = new FormData();

  formData.append("image", file);

  const response = await api.post<AtlasResult>(
    "/atlas/analyze",
    formData
  );

  return response.data;
};


// ============================================================
// SIMULATION
// ============================================================

export type SimulationScenario =
  | "critical_node"
  | "critical_edge"
  | "node"
  | "edge";

export const runSimulation = async (
  scenario: SimulationScenario,
  node?: [number, number],
  edge?: [[number, number], [number, number]]
): Promise<SimulationResult> => {
  const response = await api.post<SimulationResult>(
    "/atlas/simulate",
    {
      scenario,
      node: node ?? null,
      edge: edge ?? null,
    }
  );

  return response.data;
};