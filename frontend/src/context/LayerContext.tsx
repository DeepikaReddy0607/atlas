import {
  createContext,
  useContext,
  useCallback,
  useMemo,
  type ReactNode,
} from "react";

import type { Layer } from "../types/layer";
import { useWorkspace } from "./WorkspaceContext";

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
  const {
    activeWorkspace,
    updateWorkspace,
  } = useWorkspace();

  const layers = activeWorkspace.layers;

  /* ==========================================================
     Set Layers
  ========================================================== */

  const setLayers = useCallback<
    React.Dispatch<React.SetStateAction<Layer[]>>
  >(
    (value) => {
      updateWorkspace(
        activeWorkspace.id,
        {
          layers:
            typeof value === "function"
              ? value(activeWorkspace.layers)
              : value,
        }
      );
    },
    [
      activeWorkspace.id,
      activeWorkspace.layers,
      updateWorkspace,
    ]
  );

  /* ==========================================================
     Toggle Layer
  ========================================================== */

  const toggleLayer = useCallback(
    (id: string) => {
      updateWorkspace(
        activeWorkspace.id,
        {
          layers:
            activeWorkspace.layers.map(
              (layer) =>
                layer.id === id
                  ? {
                      ...layer,
                      visible:
                        !layer.visible,
                    }
                  : layer
            ),
        }
      );
    },
    [
      activeWorkspace.id,
      activeWorkspace.layers,
      updateWorkspace,
    ]
  );

  /* ==========================================================
     Update Opacity
  ========================================================== */

  const updateOpacity = useCallback(
    (
      id: string,
      opacity: number
    ) => {
      updateWorkspace(
        activeWorkspace.id,
        {
          layers:
            activeWorkspace.layers.map(
              (layer) =>
                layer.id === id
                  ? {
                      ...layer,
                      opacity,
                    }
                  : layer
            ),
        }
      );
    },
    [
      activeWorkspace.id,
      activeWorkspace.layers,
      updateWorkspace,
    ]
  );

  /* ==========================================================
     Reset Layers
  ========================================================== */

  const resetLayers = useCallback(() => {
    updateWorkspace(
      activeWorkspace.id,
      {
        layers:
          activeWorkspace.layers.map(
            (layer) => ({
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
            })
          ),
      }
    );
  }, [
    activeWorkspace.id,
    activeWorkspace.layers,
    updateWorkspace,
  ]);

  /* ==========================================================
     Context Value
  ========================================================== */

  const value = useMemo<LayerContextType>(
    () => ({
      layers,
      setLayers,
      toggleLayer,
      updateOpacity,
      resetLayers,
    }),
    [
      layers,
      setLayers,
      toggleLayer,
      updateOpacity,
      resetLayers,
    ]
  );

  return (
    <LayerContext.Provider value={value}>
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