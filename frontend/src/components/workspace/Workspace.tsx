import {
  Map,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Crosshair,
  Layers3,
  Plus,
} from "lucide-react";
import {
  useRef,
  useState,
  type WheelEvent,
  type PointerEvent,
} from "react";

import { useWorkspace } from "../../context/WorkspaceContext";
import { useLayers } from "../../context/LayerContext";

import "./workspace.css";

const API_BASE_URL = "http://localhost:8000";

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 5;

interface WorkspaceProps {
  onNewAnalysis: () => void;
  hasAnalysis: boolean;
}

const Workspace = ({
  onNewAnalysis,
  hasAnalysis,
}: WorkspaceProps) => {
    if (!hasAnalysis) {
    return (
      <div
        className="
          flex
          h-full
          w-full
          items-center
          justify-center
          bg-[#020906]
        "
      >
        <div
          className="
            flex
            max-w-md
            flex-col
            items-center
            text-center
          "
        >
          <div
            className="
              mb-5
              flex
              h-14
              w-14
              items-center
              justify-center
              rounded-xl
              border
              border-[#183522]
              bg-[#07130c]
            "
          >
            <Plus size={22} />
          </div>

          <span
            className="
              mb-2
              font-mono
              text-[10px]
              uppercase
              tracking-[0.18em]
              text-[#526f4b]
            "
          >
            WORKSPACE READY
          </span>

          <h2
            className="
              text-xl
              font-medium
              text-[#E8F0E8]
            "
          >
            No analysis in this workspace
          </h2>

          <p
            className="
              mt-2
              max-w-sm
              text-sm
              leading-6
              text-[#718174]
            "
          >
            Import satellite imagery to initialize
            the ATLAS intelligence pipeline.
          </p>

          <button
            type="button"
            onClick={onNewAnalysis}
            className="
              mt-6
              flex
              items-center
              gap-2
              rounded-lg
              border
              border-[#31563b]
              bg-[#0b1b11]
              px-5
              py-2.5
              text-sm
              font-medium
              text-[#dce9dd]
              transition
              hover:border-[#526f4b]
              hover:bg-[#102619]
            "
          >
            <Plus size={16} />
            New Analysis
          </button>
        </div>
      </div>
    );
  }
  const { activeWorkspace } = useWorkspace();

const { analysisResult } = activeWorkspace;
  const { layers } = useLayers();

  // =========================================================
  // VIEW STATE
  // =========================================================

  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);

  // =========================================================
  // POINTER STATE
  // =========================================================

  const imageAreaRef = useRef<HTMLDivElement | null>(null);

  const draggingRef = useRef(false);

  const dragStartRef = useRef({
    x: 0,
    y: 0,
  });

  const panStartRef = useRef({
    x: 0,
    y: 0,
  });

  // =========================================================
  // ZOOM
  // =========================================================

  const zoomIn = () => {
    setZoom((current) =>
      Math.min(
        current * 1.25,
        MAX_ZOOM
      )
    );
  };

  const zoomOut = () => {
    setZoom((current) =>
      Math.max(
        current / 1.25,
        MIN_ZOOM
      )
    );
  };

  // =========================================================
  // RESET
  // =========================================================

  const resetView = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  };

  // =========================================================
  // MOUSE WHEEL ZOOM
  // =========================================================

  const handleWheel = (
    event: WheelEvent<HTMLDivElement>
  ) => {
    event.preventDefault();

    const direction =
      event.deltaY > 0 ? 0.9 : 1.1;

    setZoom((current) =>
      Math.min(
        Math.max(
          current * direction,
          MIN_ZOOM
        ),
        MAX_ZOOM
      )
    );
  };

  // =========================================================
  // POINTER DOWN
  // =========================================================

  const handlePointerDown = (
    event: PointerEvent<HTMLDivElement>
  ) => {
    // Only primary mouse button
    if (event.button !== 0) {
      return;
    }

    draggingRef.current = true;

    dragStartRef.current = {
      x: event.clientX,
      y: event.clientY,
    };

    panStartRef.current = {
      x: panX,
      y: panY,
    };

    event.currentTarget.setPointerCapture(
      event.pointerId
    );
  };

  // =========================================================
  // POINTER MOVE
  // =========================================================

  const handlePointerMove = (
    event: PointerEvent<HTMLDivElement>
  ) => {
    if (!draggingRef.current) {
      return;
    }

    const deltaX =
      event.clientX -
      dragStartRef.current.x;

    const deltaY =
      event.clientY -
      dragStartRef.current.y;

    setPanX(
      panStartRef.current.x + deltaX
    );

    setPanY(
      panStartRef.current.y + deltaY
    );
  };

  // =========================================================
  // POINTER UP
  // =========================================================

  const handlePointerUp = (
    event: PointerEvent<HTMLDivElement>
  ) => {
    draggingRef.current = false;

    if (
      event.currentTarget.hasPointerCapture(
        event.pointerId
      )
    ) {
      event.currentTarget.releasePointerCapture(
        event.pointerId
      );
    }
  };

  // =========================================================
  // POINTER CANCEL
  // =========================================================

  const handlePointerCancel = () => {
    draggingRef.current = false;
  };

  // =========================================================
  // FULLSCREEN
  // =========================================================

  const toggleFullscreen = async () => {
    const element =
      imageAreaRef.current;

    if (!element) {
      return;
    }

    try {
      if (!document.fullscreenElement) {
        await element.requestFullscreen();
      } else {
        await document.exitFullscreen();
      }
    } catch (error) {
      console.error(
        "ATLAS fullscreen failed:",
        error
      );
    }
  };

  // =========================================================
  // URL RESOLUTION
  // =========================================================

  const resolveLayerUrl = (
    url: string | null | undefined
  ): string | null => {
    if (!url) {
      return null;
    }

    if (
      url.startsWith("http://") ||
      url.startsWith("https://") ||
      url.startsWith("blob:")
    ) {
      return url;
    }

    if (url.startsWith("/")) {
      return `${API_BASE_URL}${url}`;
    }

    return `${API_BASE_URL}/${url}`;
  };

  // =========================================================
  // SEGMENTATION
  // =========================================================

  const segmentationOverlay =
    analysisResult?.visualizations
      ?.segmentation_overlay ?? null;

  const segmentationOverlayUrl =
    resolveLayerUrl(
      segmentationOverlay
    );

  // =========================================================
  // BASE IMAGE
  // =========================================================

  const baseLayer = layers.find(
    (layer) => layer.type === "base"
  );

  const baseImageUrl =
    resolveLayerUrl(
      baseLayer?.url
    ) ??
    segmentationOverlayUrl;

  // =========================================================
  // PROCESSED LAYERS
  // =========================================================

  const processedLayers =
    layers.filter(
      (layer) =>
        layer.type !== "base"
    );

  return (
    <main className="atlas-workspace">

      {/* =====================================================
          MAIN CANVAS
      ====================================================== */}

      <section className="atlas-workspace__canvas">

        <div className="atlas-workspace__canvas-grid" />

        {/* =================================================
            CANVAS HEADER
        ================================================= */}

        <div className="atlas-workspace__canvas-header">

          <div className="atlas-workspace__canvas-title">

            <span className="atlas-status-dot" />

            <span>
              SATELLITE IMAGERY
            </span>

          </div>

          <span className="atlas-workspace__canvas-meta">
            GEO-01 / ANALYSIS 01
          </span>

        </div>

        {/* =================================================
            IMAGE AREA
        ================================================= */}

        <div
          ref={imageAreaRef}
          className="atlas-workspace__image-area"
          onWheel={handleWheel}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerCancel={
            handlePointerCancel
          }
          style={{
            cursor: draggingRef.current
              ? "grabbing"
              : zoom > 1
              ? "grab"
              : "default",
          }}
        >

          {/* =================================================
              TRANSFORMED IMAGE GROUP
          ================================================= */}

          <div
            style={{
              position: "absolute",
              inset: 0,

              transform: `
                translate(${panX}px, ${panY}px)
                scale(${zoom})
              `,

              transformOrigin:
                "center center",

              transition:
                draggingRef.current
                  ? "none"
                  : "transform 180ms ease",

              pointerEvents: "none",
            }}
          >

            {/* =============================================
                BASE IMAGE
            ============================================= */}

            {baseImageUrl ? (
              <img
                src={baseImageUrl}
                alt="ATLAS satellite imagery"
                className="atlas-workspace__analysis-image"
                draggable={false}
                onError={() => {
                  console.error(
                    "ATLAS base image failed to load:",
                    baseImageUrl
                  );
                }}
              />
            ) : (
                <div className="atlas-workspace__empty-map">

                  <Map
                    size={34}
                    strokeWidth={1}
                  />

                  <strong>
                    No analysis loaded
                  </strong>

                  <span>
                    This workspace is ready for a new
                    infrastructure analysis.
                  </span>

                  <button
                    type="button"
                    onClick={onNewAnalysis}
                    className="
                      mt-4
                      inline-flex
                      items-center
                      justify-center
                      rounded-md
                      border
                      border-[var(--atlas-border)]
                      bg-[var(--atlas-surface)]
                      px-4
                      py-2
                      text-sm
                      font-medium
                      text-[var(--atlas-text)]
                      transition
                      hover:bg-white/10
                      active:scale-[0.98]
                    "
                  >
                    Start New Analysis
                  </button>

                </div>
            )}

            {/* =============================================
                PROCESSED LAYERS
            ============================================= */}

            {processedLayers.map(
              (layer) => {

                const layerUrl =
                  resolveLayerUrl(
                    layer.url
                  );

                if (
                  !layerUrl ||
                  !layer.visible
                ) {
                  return null;
                }

                return (
                  <img
                    key={layer.id}
                    src={layerUrl}
                    alt={layer.name}
                    className="atlas-workspace__layer-image"
                    style={{
                      opacity:
                        layer.opacity,
                    }}
                    draggable={false}
                    onError={() => {
                      console.error(
                        `ATLAS layer failed to load: ${layer.name}`,
                        layerUrl
                      );
                    }}
                  />
                );
              }
            )}

          </div>

          {/* =================================================
              MAP CONTROLS
          ================================================= */}

          <div
            className="atlas-workspace__map-controls"
            onPointerDown={(event) =>
              event.stopPropagation()
            }
          >

            <button
              type="button"
              aria-label="Zoom in"
              onClick={zoomIn}
            >
              <ZoomIn size={16} />
            </button>

            <button
              type="button"
              aria-label="Zoom out"
              onClick={zoomOut}
            >
              <ZoomOut size={16} />
            </button>

            <button
              type="button"
              aria-label="Reset view"
              onClick={resetView}
            >
              <Crosshair size={16} />
            </button>

            <button
              type="button"
              aria-label="Fullscreen"
              onClick={
                toggleFullscreen
              }
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