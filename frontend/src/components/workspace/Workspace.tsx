import { useEffect, useMemo, useState } from "react";

import UploadZone from "../upload/UploadZone";
import ImageViewer from "./ImageViewer";
import OverlayViewer from "./OverlayViewer";
import LayerPanel from "./LayerPanel";

import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import type { Layer } from "../../types/layer";

const Workspace = () => {
  const {
    selectedFile,
    analysisResult,
    analyze,
    loading,
  } = useAtlasAnalysis();

  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const [layers, setLayers] = useState<Layer[]>([
    {
      id: "satellite",
      name: "Satellite",
      visible: true,
      opacity: 1,
    },
    {
      id: "segmentation",
      name: "Segmentation",
      visible: true,
      opacity: 0.65,
    },
  ]);

  useEffect(() => {
    if (!selectedFile) {
      setImageUrl(null);
      return;
    }

    const url = URL.createObjectURL(selectedFile);
    setImageUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  const overlayUrl = useMemo(() => {
    if (
      !analysisResult ||
      !analysisResult.visualizations.segmentation_overlay
    ) {
      return null;
    }

    return `http://127.0.0.1:8000${analysisResult.visualizations.segmentation_overlay}`;
  }, [analysisResult]);

  const segmentationLayer = layers.find(
    (layer) => layer.id === "segmentation"
  );

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

  return (
    <main
      className="
        relative
        flex-1
        overflow-hidden
        bg-[var(--atlas-bg)]
      "
    >
      {!selectedFile && (
        <div className="h-full p-8">
          <UploadZone
            onFileSelected={analyze}
          />
        </div>
      )}

      {selectedFile && imageUrl && !overlayUrl && (
        <ImageViewer file={selectedFile} />
      )}

      {selectedFile && imageUrl && overlayUrl && (
        <>
          <OverlayViewer
            imageUrl={imageUrl}
            overlayUrl={overlayUrl}
            opacity={segmentationLayer?.opacity ?? 0.65}
            showOverlay={
              segmentationLayer?.visible ?? true
            }
          />

          <LayerPanel
            layers={layers}
            onToggle={toggleLayer}
            onOpacityChange={updateOpacity}
          />
        </>
      )}

      {loading && (
        <div
          className="
            absolute
            inset-0
            flex
            items-center
            justify-center
            bg-black/40
            backdrop-blur-sm
            z-50
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
            <h2 className="mb-3 text-xl font-semibold">
              Analyzing Satellite Image...
            </h2>

            <p className="text-[var(--atlas-text-muted)]">
              Running AI segmentation...
            </p>
          </div>
        </div>
      )}
    </main>
  );
};

export default Workspace;