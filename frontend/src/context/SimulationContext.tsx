import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import type { SimulationResult } from "../types/atlas";

export type SimulationScenario =
  | "flood"
  | "earthquake"
  | "bridge"
  | "critical";

interface SimulationContextType {
  selectedScenario: SimulationScenario;
  setSelectedScenario: (
    scenario: SimulationScenario
  ) => void;

  running: boolean;
  setRunning: (running: boolean) => void;

  result: SimulationResult | null;
  setResult: (result: SimulationResult | null) => void;

  error: string | null;
  setError: (error: string | null) => void;
}

const SimulationContext =
  createContext<SimulationContextType | undefined>(
    undefined
  );

export const SimulationProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [selectedScenario, setSelectedScenario] =
    useState<SimulationScenario>("critical");

  const [running, setRunning] = useState(false);

  const [result, setResult] =
    useState<SimulationResult | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  return (
    <SimulationContext.Provider
      value={{
        selectedScenario,
        setSelectedScenario,
        running,
        setRunning,
        result,
        setResult,
        error,
        setError,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
};

export const useSimulation = () => {
  const context = useContext(SimulationContext);

  if (!context) {
    throw new Error(
      "useSimulation must be used inside SimulationProvider"
    );
  }

  return context;
};