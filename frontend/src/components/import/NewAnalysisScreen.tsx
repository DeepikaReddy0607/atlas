import {
  ArrowLeft,
  ArrowRight,
  Radar,
} from "lucide-react";
import { useState } from "react";

import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import AtlasLogo from "../welcome/AtlasLogo";
import ImageDropZone from "./ImageDropZone";
import ImagePreviewCard from "./ImagePreviewCard";
import "./new-analysis.css";

interface NewAnalysisScreenProps {
  onBack: () => void;
  onStartAnalysis: () => void;
}

const NewAnalysisScreen = ({
  onBack,
  onStartAnalysis,
}: NewAnalysisScreenProps) => {
  const [pendingFile, setPendingFile] = useState<File | null>(null);

  const { analyze } = useAtlasAnalysis();

  const startAnalysis = () => {
    if (!pendingFile) return;

    void analyze(pendingFile);
    onStartAnalysis();
  };

  return (
    <main
      className="atlas-import"
      aria-labelledby="new-analysis-title"
    >
      {/* =====================================================
          BACKGROUND SYSTEM
      ===================================================== */}

      <div
        className="atlas-import__grid"
        aria-hidden="true"
      />

      <div
        className="atlas-import__contours"
        aria-hidden="true"
      />

      <div
        className="atlas-import__radar"
        aria-hidden="true"
      />

      {/* =====================================================
          GEO TELEMETRY
      ===================================================== */}

      <div
        className="atlas-import__coordinates"
        aria-hidden="true"
      >
        <span>34° 56′ 12″ N</span>
        <span>78° 14′ 45″ E</span>
      </div>

      <div
        className="atlas-import__system-id"
        aria-hidden="true"
      >
        <span>ATLAS / GEO-01</span>
        <span>IMPORT MODULE</span>
      </div>

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="atlas-import__header">
        <AtlasLogo size="compact" />

        <div className="atlas-import__header-meta">
          <span className="atlas-import__status-dot" />
          <span>NEW ANALYSIS</span>
          <i>/</i>
          <span>IMAGERY INGEST</span>
        </div>
      </header>

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <section className="atlas-import__content">

        {/* Heading */}

        <div className="atlas-import__heading">

          <div className="atlas-import__eyebrow">
            <Radar
              size={13}
              strokeWidth={1.7}
              aria-hidden="true"
            />

            <span>GEOSPATIAL INPUT</span>
          </div>

          <h1 id="new-analysis-title">
            Import satellite
            <br />
            <strong>imagery.</strong>
          </h1>

          <div className="atlas-import__accent-line" />

          <p className="atlas-import__intro">
            Select a satellite image to initialize
            infrastructure, terrain, and resilience analysis.
          </p>

        </div>

        {/* ===================================================
            IMPORT WORKSPACE
        =================================================== */}

        <div className="atlas-import__workspace">

          <div className="atlas-import__panel">

            {/* Panel header */}

            <div className="atlas-import__panel-top">

              <span>
                <span className="atlas-import__live-dot" />
                IMAGE SOURCE
              </span>

              <span>
                INPUT / 01
              </span>

            </div>

            {/* Upload / Preview */}

            <div className="atlas-import__drop-area">

              {!pendingFile ? (

                <ImageDropZone
                  onFileSelected={setPendingFile}
                />

              ) : (

                <ImagePreviewCard
                  file={pendingFile}
                  onChange={() => setPendingFile(null)}
                  onRemove={() => setPendingFile(null)}
                />

              )}

            </div>

            {/* Panel footer */}

            {!pendingFile && (
              <div className="atlas-import__panel-bottom">

                <div className="atlas-import__formats">
                  <span>SUPPORTED</span>
                  <b>JPG</b>
                  <b>PNG</b>
                  <b>WEBP</b>
                  <b>TIFF</b>
                </div>

                <span className="atlas-import__security">
                  LOCAL PROCESSING
                </span>

              </div>
            )}

          </div>

        </div>

        {/* ===================================================
            NAVIGATION
        =================================================== */}

        <div className="atlas-import__navigation">

          <button
            type="button"
            className="atlas-import__back"
            onClick={onBack}
          >
            <ArrowLeft
              size={15}
              aria-hidden="true"
            />

            <span>BACK</span>
          </button>

          {pendingFile && (
            <button
              type="button"
              className="atlas-import__start"
              onClick={startAnalysis}
            >
              <span>START ANALYSIS</span>

              <ArrowRight
                size={17}
                aria-hidden="true"
              />
            </button>
          )}

        </div>

      </section>

      {/* =====================================================
          FOOTER TELEMETRY
      ===================================================== */}

      <footer className="atlas-import__footer">

        <div>
          <span className="atlas-import__footer-dot" />
          SYSTEM READY
        </div>

        <div className="atlas-import__footer-center">
          IMAGE INGEST
          <i>→</i>
          SEGMENTATION
          <i>→</i>
          NETWORK
          <i>→</i>
          RESILIENCE
        </div>

        <div>
          ATLAS / 01
        </div>

      </footer>

    </main>
  );
};

export default NewAnalysisScreen;