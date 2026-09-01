import type { ReactNode } from "react";
import { toast } from "sonner";

import { analyzeImage } from "../api/atlasApi";
import { useWorkspace } from "../context/WorkspaceContext";

import type { AtlasResult } from "../types/atlas";
import type { Layer } from "../types/layer";

import {
  AtlasAnalysisContext,
} from "../context/AtlasAnalysisContext";

interface Props {
  children: ReactNode;
}

const AtlasAnalysisProvider = ({
  children,
}: Props) => {
  const {
    activeWorkspace,
    updateWorkspace,
  } = useWorkspace();

  const selectedFile =
    activeWorkspace.selectedFile;

  const analysisResult =
    activeWorkspace.analysisResult;

  const loading =
    activeWorkspace.loading;

  const error =
    activeWorkspace.error;

  const analyze = async (file: File) => {
    const workspaceId =
      activeWorkspace.id;

    try {
      updateWorkspace(
        workspaceId,
        {
          selectedFile: file,
          loading: true,
          error: null,
        }
      );

      toast.loading(
        "Analyzing satellite image...",
        {
          id: "analysis",
        }
      );

      const result =
        (await analyzeImage(file)) as AtlasResult;

      const visualizations =
        result.visualizations;

      const layers: Layer[] = [];

      /*
       * -------------------------------------------------------
       * Base segmentation / imagery
       * -------------------------------------------------------
       */

      if (visualizations.segmentation_overlay) {
        layers.push({
          id: "segmentation",
          name: "Segmentation",
          url: visualizations.segmentation_overlay,
          visible: true,
          opacity: 1,
          type: "overlay",
        });
      }

      /*
       * -------------------------------------------------------
       * Road mask
       * -------------------------------------------------------
       */

      if (visualizations.road_mask) {
        layers.push({
          id: "road-mask",
          name: "Road Mask",
          url: visualizations.road_mask,
          visible: false,
          opacity: 0.85,
          type: "mask",
        });
      }

      /*
       * -------------------------------------------------------
       * Skeleton
       * -------------------------------------------------------
       */

      if (visualizations.skeleton) {
        layers.push({
          id: "skeleton",
          name: "Road Skeleton",
          url: visualizations.skeleton,
          visible: false,
          opacity: 0.9,
          type: "analysis",
        });
      }

      /*
       * -------------------------------------------------------
       * Graph
       * -------------------------------------------------------
       */

      if (visualizations.graph) {
        layers.push({
          id: "graph",
          name: "Topology Graph",
          url: visualizations.graph,
          visible: false,
          opacity: 0.9,
          type: "graph",
        });
      }

      /*
       * -------------------------------------------------------
       * Criticality
       * -------------------------------------------------------
       */

      if (visualizations.criticality) {
        layers.push({
          id: "criticality",
          name: "Criticality",
          url: visualizations.criticality,
          visible: false,
          opacity: 0.9,
          type: "analysis",
        });
      }

      updateWorkspace(
        workspaceId,
        {
          analysisResult: result,
          loading: false,
          error: null,
          layers,
          selectedLayerId:
            layers.length > 0
              ? layers[0].id
              : null,
        }
      );

      toast.success(
        "Analysis completed successfully!",
        {
          id: "analysis",
        }
      );
    } catch (err) {
      console.error(
        "Provider error:",
        err
      );

      updateWorkspace(
        workspaceId,
        {
          loading: false,
          error: "Analysis failed.",
        }
      );

      toast.error(
        "Analysis failed.",
        {
          id: "analysis",
        }
      );
    }
  };

  return (
    <AtlasAnalysisContext.Provider
      value={{
        selectedFile,
        analysisResult,
        loading,
        error,
        analyze,
      }}
    >
      {children}
    </AtlasAnalysisContext.Provider>
  );
};

export default AtlasAnalysisProvider;