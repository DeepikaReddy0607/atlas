import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import type { Layer } from "../types/layer";

interface LayerContextType {
  layers: Layer[];

  setLayers: React.Dispatch<
    React.SetStateAction<Layer[]>
  >;

  toggleLayer: (id: string) => void;

  updateOpacity: (
    id: string,
    opacity: number
  ) => void;

  resetLayers: () => void;
}

const LayerContext =
  createContext<LayerContextType | null>(null);

export function LayerProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [layers, setLayers] =
    useState<Layer[]>([]);

  const toggleLayer = (id: string) => {
    setLayers((prev) =>
      prev.map((layer) =>
        layer.id === id
          ? {
              ...layer,
              visible: !layer.visible,
            }
          : layer
      )
    );
  };

  const updateOpacity = (
    id: string,
    opacity: number
  ) => {
    setLayers((prev) =>
      prev.map((layer) =>
        layer.id === id
          ? {
              ...layer,
              opacity,
            }
          : layer
      )
    );
  };

  const resetLayers = () => {
    setLayers((prev) =>
      prev.map((layer) => ({
        ...layer,
        visible:
          layer.type === "base"
            ? true
            : false,
        opacity:
          layer.type === "overlay"
            ? 0.65
            : layer.type === "mask"
            ? 0.85
            : 1,
      }))
    );
  };

  return (
    <LayerContext.Provider
      value={{
        layers,
        setLayers,
        toggleLayer,
        updateOpacity,
        resetLayers,
      }}
    >
      {children}
    </LayerContext.Provider>
  );
}

export function useLayers() {
  const context =
    useContext(LayerContext);

  if (!context) {
    throw new Error(
      "useLayers must be used inside LayerProvider"
    );
  }

  return context;
}