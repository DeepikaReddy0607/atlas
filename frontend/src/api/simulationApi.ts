import api from "./axios";
import type { SimulationResult } from "../types/atlas";

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