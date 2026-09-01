import {
  Map,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Crosshair,
  Layers3,
} from "lucide-react";

import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import { useLayers } from "../../context/LayerContext";

import "./workspace.css";

const API_BASE_URL = "http://localhost:8000";

interface WorkspaceProps {
  onNewAnalysis?: () => void;
}

const Workspace = ({ onNewAnalysis }: WorkspaceProps) => {
  const { analysisResult } = useAtlasAnalysis();
  const { layers } = useLayers();

  /*
   * ---------------------------------------------------------
   * Backend segmentation visualization
   * ---------------------------------------------------------
   */

  const segmentationOverlay =
    analysisResult?.visualizations?.segmentation_overlay ?? null;

  const segmentationOverlayUrl = segmentationOverlay
    ? `${API_BASE_URL}${segmentationOverlay}`
    : null;

  /*
   * ---------------------------------------------------------
   * Resolve layer URL
   *
   * The LayerContext is now the source of truth for
   * visibility + opacity.
   * ---------------------------------------------------------
   */

  const resolveLayerUrl = (layer: (typeof layers)[number]) => {
    if (!layer.url) {
      return null;
    }

    if (layer.url.startsWith("http://")) {
      return layer.url;
    }

    if (layer.url.startsWith("https://")) {
      return layer.url;
    }

    return `${API_BASE_URL}${layer.url}`;
  };

  /*
   * ---------------------------------------------------------
   * Base image
   *
   * Keep the segmentation visualization as the fallback
   * because that is what the current backend already provides.
   * ---------------------------------------------------------
   */

  const baseLayer =
    layers.find((layer) => layer.type === "base");

  const baseImageUrl =
    baseLayer?.url
      ? resolveLayerUrl(baseLayer)
      : segmentationOverlayUrl;

  /*
   * ---------------------------------------------------------
   * Processed layers
   * ---------------------------------------------------------
   */

  const processedLayers = layers.filter(
    (layer) => layer.type !== "base"
  );

  return (
    <main className="atlas-workspace">

      {/* =====================================================
          MAIN CANVAS
      ===================================================== */}

      <section className="atlas-workspace__canvas">

        <div className="atlas-workspace__canvas-grid" />

        {/* =================================================
            CANVAS HEADER
        ================================================= */}

        <div className="atlas-workspace__canvas-header">

          <div className="atlas-workspace__canvas-title">
            <span className="atlas-status-dot" />
            <span>SATELLITE IMAGERY</span>
          </div>

          <span className="atlas-workspace__canvas-meta">
            GEO-01 / ANALYSIS 01
          </span>

        </div>


        {/* =================================================
            IMAGE / NETWORK AREA
        ================================================= */}

        <div className="atlas-workspace__image-area">

          {/* =================================================
              BASE IMAGE
          ================================================= */}

          {baseImageUrl ? (
            <img
              src={baseImageUrl}
              alt="ATLAS satellite imagery"
              className="atlas-workspace__analysis-image"
            />
          ) : (
            <div className="atlas-workspace__empty-map">

              <Map
                size={34}
                strokeWidth={1}
              />

              <strong>
                Imagery canvas
              </strong>

              <span>
                Analysis visualization will appear here
              </span>

            </div>
          )}


          {/* =================================================
              PROCESSED LAYERS
              
              IMPORTANT:
              These are absolutely positioned on top of the
              base image. They are NOT separate images in flow.
          ================================================= */}

          {processedLayers.map((layer) => {

            const layerUrl = resolveLayerUrl(layer);

            if (!layerUrl || !layer.visible) {
              return null;
            }

            return (
              <img
                key={layer.id}
                src={layerUrl}
                alt={layer.name}
                className="atlas-workspace__layer-image"
                style={{
                  opacity: layer.opacity,
                }}
              />
            );
          })}


          {/* =================================================
              MAP CONTROLS
          ================================================= */}

          <div className="atlas-workspace__map-controls">

            <button
              type="button"
              aria-label="Zoom in"
            >
              <ZoomIn size={16} />
            </button>

            <button
              type="button"
              aria-label="Zoom out"
            >
              <ZoomOut size={16} />
            </button>

            <button
              type="button"
              aria-label="Reset view"
            >
              <Crosshair size={16} />
            </button>

            <button
              type="button"
              aria-label="Fullscreen"
            >
              <Maximize2 size={16} />
            </button>

          </div>

        </div>


        {/* =================================================
            LAYERS BUTTON
        ================================================= */}

        <button
          type="button"
          className="atlas-workspace__layers"
        >
          <Layers3
            size={15}
            strokeWidth={1.3}
          />

          Layers
        </button>


        {/* =================================================
            REGION LABEL
        ================================================= */}

        <div className="atlas-workspace__map-label">

          <span />

          REGION ANALYSIS

        </div>


        {/* =================================================
            SCALE
        ================================================= */}

        <div className="atlas-workspace__scale">

          <div className="atlas-workspace__scale-line" />

          <div>
            <span>0</span>
            <span>500 m</span>
            <span>1 km</span>
            <span>2 km</span>
          </div>

        </div>

      </section>

    </main>
  );
};

export default Workspace;