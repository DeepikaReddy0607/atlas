import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

interface LayerSelectionContextType {
  selectedLayerId: string;
  setSelectedLayerId: (id: string) => void;
}

const LayerSelectionContext = createContext<
  LayerSelectionContextType | undefined
>(undefined);

export const LayerSelectionProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [selectedLayerId, setSelectedLayerId] =
    useState("segmentation");

  return (
    <LayerSelectionContext.Provider
      value={{
        selectedLayerId,
        setSelectedLayerId,
      }}
    >
      {children}
    </LayerSelectionContext.Provider>
  );
};

export const useLayerSelection = () => {
  const context = useContext(
    LayerSelectionContext
  );

  if (!context) {
    throw new Error(
      "useLayerSelection must be used inside LayerSelectionProvider"
    );
  }

  return context;
};