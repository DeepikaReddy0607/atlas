import api from "./axios";

import type {
  SimulationResult,
} from "../types/atlas";

import type {
  SimulationScenario,
} from "../context/SimulationContext";

export const runSimulation = async (
  scenario: SimulationScenario
): Promise<SimulationResult> => {
  const response = await api.post(
    "/atlas/simulate",
    {
      scenario,
    }
  );

  return response.data;
};