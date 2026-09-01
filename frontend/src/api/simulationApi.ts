import api from "./axios";

export const runSimulation = async (scenario: string) => {
  const response = await api.post("/atlas/simulate", {
    scenario,
  });

  return response.data;
};