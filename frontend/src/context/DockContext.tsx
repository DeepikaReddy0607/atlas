import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

export type DockTab =
  | "imagery"
  | "ai"
  | "graph"
  | "map"
  | "risk"
  | "simulation"
  | "report"
  | "settings";

interface DockContextType {
  activeTab: DockTab;
  setActiveTab: (tab: DockTab) => void;
}

const DockContext =
  createContext<DockContextType | null>(null);

export function DockProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [activeTab, setActiveTab] =
    useState<DockTab>("imagery");

  return (
    <DockContext.Provider
      value={{
        activeTab,
        setActiveTab,
      }}
    >
      {children}
    </DockContext.Provider>
  );
}

export function useDock() {
  const context = useContext(DockContext);

  if (!context) {
    throw new Error(
      "useDock must be used inside DockProvider"
    );
  }

  return context;
}