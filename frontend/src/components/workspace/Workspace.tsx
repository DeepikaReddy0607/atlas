import { useEffect, useState } from "react";

import UploadZone from "../upload/UploadZone";
import ImageViewer from "./ImageViewer";
import OverlayViewer from "./OverlayViewer";
import LayerPanel from "./LayerPanel";

import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import { useLayers } from "../../context/LayerContext";
import { useAtlasSettings } from "../../hooks/useAtlasSettings";

import type { Layer } from "../../types/layer";

const Workspace = () => {
  const {
    selectedFile,
    analysisResult,
    analyze,
    loading,
  } = useAtlasAnalysis();

  const settings = useAtlasSettings();

  const {
    layers,
    setLayers,
  } = useLayers();

  const [imageUrl, setImageUrl] =
    useState<string | null>(null);

  // ---------------------------------------------------------
  // Create object URL for uploaded image
  // ---------------------------------------------------------

  useEffect(() => {
    if (!selectedFile) {
      setImageUrl(null);
      return;
    }

    const url =
      URL.createObjectURL(selectedFile);

    setImageUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [selectedFile]);

  // ---------------------------------------------------------
  // Build visualization layers
  // ---------------------------------------------------------

  useEffect(() => {
    if (!analysisResult || !imageUrl) {
      return;
    }

    const baseUrl =
      "http://127.0.0.1:8000";

    const visualizationLayers: Layer[] = [
      // -----------------------------------------------------
      // Base satellite image
      // -----------------------------------------------------

      {
        id: "satellite",
        name: "Satellite",
        url: imageUrl,
        visible: true,
        opacity: 1,
        type: "base",
      },

      // -----------------------------------------------------
      // AI segmentation
      // -----------------------------------------------------

      {
        id: "segmentation",
        name: "Segmentation",
        url:
          analysisResult.visualizations
            .segmentation_overlay
            ? `${baseUrl}${analysisResult.visualizations.segmentation_overlay}`
            : undefined,
        visible: settings.showSegmentation,
        opacity: settings.overlayOpacity,
        type: "overlay",
      },

      // -----------------------------------------------------
      // Road mask
      // -----------------------------------------------------

      {
        id: "road_mask",
        name: "Road Mask",
        url:
          analysisResult.visualizations
            .road_mask
            ? `${baseUrl}${analysisResult.visualizations.road_mask}`
            : undefined,
        visible: false,
        opacity: 0.85,
        type: "mask",
      },

      // -----------------------------------------------------
      // Skeleton
      // -----------------------------------------------------

      {
        id: "skeleton",
        name: "Skeleton",
        url:
          analysisResult.visualizations
            .skeleton
            ? `${baseUrl}${analysisResult.visualizations.skeleton}`
            : undefined,
        visible: false,
        opacity: 0.85,
        type: "mask",
      },

      // -----------------------------------------------------
      // Topology graph
      // -----------------------------------------------------

      {
        id: "graph",
        name: "Graph",
        url:
          analysisResult.visualizations
            .graph
            ? `${baseUrl}${analysisResult.visualizations.graph}`
            : undefined,
        visible: settings.showGraph,
        opacity: 1,
        type: "graph",
      },

      // -----------------------------------------------------
      // Criticality
      // -----------------------------------------------------

      {
        id: "criticality",
        name: "Criticality",
        url:
          analysisResult.visualizations
            .criticality
            ? `${baseUrl}${analysisResult.visualizations.criticality}`
            : undefined,
        visible: settings.showCriticality,
        opacity: 1,
        type: "analysis",
      },

      // -----------------------------------------------------
      // Simulation impact
      // -----------------------------------------------------

      {
        id: "simulation_impact",
        name: "Simulation Impact",
        visible:
          settings.showSimulationImpact,
        opacity: 1,
        type: "analysis",
      },
    ];

    // -------------------------------------------------------
    // Keep simulation layer even though it has no URL.
    // All other layers must have a backend visualization URL.
    // -------------------------------------------------------

    const filteredLayers =
      visualizationLayers.filter(
        (layer) => {
          if (
            layer.id ===
            "simulation_impact"
          ) {
            return true;
          }

          return Boolean(layer.url);
        }
      );

    setLayers(filteredLayers);
  }, [
    analysisResult,
    imageUrl,
    setLayers,

    // Settings
    settings.showSegmentation,
    settings.overlayOpacity,
    settings.showGraph,
    settings.showCriticality,
    settings.showSimulationImpact,
  ]);

  // ---------------------------------------------------------
  // Render
  // ---------------------------------------------------------

  return (
    <main
      className="
        relative
        min-h-0
        min-w-0
        flex-1
        overflow-hidden
        bg-[var(--atlas-bg)]
      "
    >
      {/* =====================================================
          No image uploaded
      ====================================================== */}

      {!selectedFile && (
        <div className="h-full p-8">
          <UploadZone
            onFileSelected={analyze}
          />
        </div>
      )}

      {/* =====================================================
          Image uploaded but analysis not available
      ====================================================== */}

      {selectedFile &&
        imageUrl &&
        layers.length === 0 && (
          <ImageViewer
            file={selectedFile}
          />
        )}

      {/* =====================================================
          Analysis available
      ====================================================== */}

      {selectedFile &&
        imageUrl &&
        layers.length > 0 && (
          <>
            <OverlayViewer
              imageUrl={imageUrl}
              layers={layers}
              graph={
                analysisResult
                  ?.topology_graph_data
              }
            />

            <LayerPanel />
          </>
        )}

      {/* =====================================================
          Analysis loading overlay
      ====================================================== */}

      {loading && (
        <div
          className="
            absolute
            inset-0
            z-50
            flex
            items-center
            justify-center
            bg-black/40
            backdrop-blur-sm
          "
        >
          <div
            className="
              rounded-xl
              bg-[var(--atlas-surface)]
              p-8
              shadow-2xl
            "
          >
            <h2
              className="
                mb-3
                text-xl
                font-semibold
              "
            >
              Analyzing Satellite Image...
            </h2>

            <p
              className="
                text-[var(--atlas-text-muted)]
              "
            >
              Running AI segmentation...
            </p>
          </div>
        </div>
      )}
    </main>
  );
};

export default Workspace;