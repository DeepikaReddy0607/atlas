import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

interface GraphSelectionContextType {
  selectedNodeId: number | null;
  setSelectedNodeId: (id: number | null) => void;
}

const GraphSelectionContext = createContext<
  GraphSelectionContextType | undefined
>(undefined);

export const GraphSelectionProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [selectedNodeId, setSelectedNodeId] =
    useState<number | null>(null);

  return (
    <GraphSelectionContext.Provider
      value={{
        selectedNodeId,
        setSelectedNodeId,
      }}
    >
      {children}
    </GraphSelectionContext.Provider>
  );
};

export const useGraphSelection = () => {
  const context = useContext(
    GraphSelectionContext
  );

  if (!context) {
    throw new Error(
      "useGraphSelection must be used inside GraphSelectionProvider"
    );
  }

  return context;
};