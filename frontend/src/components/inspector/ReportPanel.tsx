import { useState } from "react";

import {
  FileDown,
  Activity,
  Network,
  ShieldAlert,
  Brain,
  Target,
  AlertTriangle,
} from "lucide-react";

import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import { useSimulation } from "../../context/SimulationContext";
import { exportAtlasReport } from "../../api/report";

const ReportPanel = () => {
  const {
    analysisResult,
    selectedFile,
  } = useAtlasAnalysis();

  const {
    result: simulationResult,
  } = useSimulation();

  const [exporting, setExporting] =
    useState(false);

  if (!analysisResult) {
    return (
      <div
        className="
          flex
          h-full
          items-center
          justify-center
          p-6
          text-center
        "
      >
        <div>
          <FileDown
            size={42}
            className="
              mx-auto
              mb-4
              text-[var(--atlas-text-muted)]
              opacity-50
            "
          />

          <h2 className="text-lg font-semibold">
            No Report Available
          </h2>

          <p className="mt-2 text-sm text-[var(--atlas-text-muted)]">
            Run an ATLAS analysis to generate a report.
          </p>
        </div>
      </div>
    );
  }

  const {
    segmentation,
    topology_graph,
    resilience,
    risk,
    recommendation,
  } = analysisResult;

  const simulation =
    simulationResult ??
    analysisResult.simulation;

  // ---------------------------------------------------------
  // Export PDF
  // ---------------------------------------------------------

  const exportReport = async () => {
    if (!selectedFile) {
      console.error(
        "No image file available for report generation."
      );
      return;
    }

    try {
      setExporting(true);

      const blob =
        await exportAtlasReport(
          selectedFile
        );

      const url =
        window.URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = url;

      link.download =
        "atlas_infrastructure_report.pdf";

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(
        "Report export failed:",
        error
      );
    } finally {
      setExporting(false);
    }
  };

  // ---------------------------------------------------------
  // Risk styling
  // ---------------------------------------------------------

  const riskLevel =
    risk.level?.toUpperCase() ??
    "UNKNOWN";

  const riskClass =
    riskLevel === "CRITICAL"
      ? "border-red-500/40 bg-red-500/10 text-red-400"
      : riskLevel === "HIGH"
      ? "border-orange-500/40 bg-orange-500/10 text-orange-400"
      : riskLevel === "MODERATE"
      ? "border-yellow-500/40 bg-yellow-500/10 text-yellow-400"
      : "border-green-500/40 bg-green-500/10 text-green-400";

  return (
    <div
      className="
        h-full
        min-h-0
        overflow-y-auto
        p-5
      "
    >
      {/* =====================================================
          Header
      ====================================================== */}

      <div>
        <div className="flex items-center gap-2">
          <FileDown size={20} />

          <h2 className="text-xl font-semibold">
            Report Export
          </h2>
        </div>

        <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
          Analysis summary and report generation
        </p>
      </div>

      {/* =====================================================
          Executive Summary
      ====================================================== */}

      <section
        className="
          mt-6
          rounded-xl
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-bg)]
          p-4
        "
      >
        <div className="mb-4 flex items-center gap-2">
          <Activity size={17} />

          <h3 className="font-semibold">
            Executive Summary
          </h3>
        </div>

        <div className="space-y-3 text-sm">
          <ReportRow
            label="Model"
            value={
              segmentation.model_name
            }
          />

          <div className="flex items-center justify-between">
            <span className="text-[var(--atlas-text-muted)]">
              Risk
            </span>

            <span
              className={`
                rounded-full
                border
                px-2.5
                py-1
                text-xs
                font-semibold
                ${riskClass}
              `}
            >
              {riskLevel}
            </span>
          </div>

          <ReportRow
            label="ARI"
            value={risk.ari.toFixed(3)}
          />
        </div>
      </section>

      {/* =====================================================
          Segmentation
      ====================================================== */}

      <section
        className="
          mt-4
          rounded-xl
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-bg)]
          p-4
        "
      >
        <div className="mb-4 flex items-center gap-2">
          <Brain size={17} />

          <h3 className="font-semibold">
            Segmentation
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Metric
            label="Model"
            value={
              segmentation.model_name
            }
          />

          <Metric
            label="Inference"
            value={`${segmentation.inference_time_ms.toFixed(
              2
            )} ms`}
          />

          <Metric
            label="Image Size"
            value={formatSize(
              segmentation.image_size
            )}
          />

          <Metric
            label="Mask Size"
            value={formatSize(
              segmentation.mask_shape
            )}
          />
        </div>
      </section>

      {/* =====================================================
          Network Topology
      ====================================================== */}

      <section
        className="
          mt-4
          rounded-xl
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-bg)]
          p-4
        "
      >
        <div className="mb-4 flex items-center gap-2">
          <Network size={17} />

          <h3 className="font-semibold">
            Network Topology
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Metric
            label="Nodes"
            value={
              topology_graph.nodes
            }
          />

          <Metric
            label="Edges"
            value={
              topology_graph.edges
            }
          />

          <Metric
            label="Components"
            value={
              resilience.connected_components
            }
          />

          <Metric
            label="Largest Component"
            value={
              resilience.largest_component
            }
          />
        </div>
      </section>

      {/* =====================================================
          Critical Infrastructure
      ====================================================== */}

      <section
        className="
          mt-4
          rounded-xl
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-bg)]
          p-4
        "
      >
        <div className="mb-4 flex items-center gap-2">
          <Target size={17} />

          <h3 className="font-semibold">
            Critical Infrastructure
          </h3>
        </div>

        <div
          className="
            rounded-lg
            border
            border-[var(--atlas-border)]
            p-3
          "
        >
          <p className="text-xs text-[var(--atlas-text-muted)]">
            Most Critical Node
          </p>

          <p className="mt-1 font-mono text-lg font-semibold">
            {formatCoordinate(
              resilience.critical_node
            )}
          </p>
        </div>
      </section>

      {/* =====================================================
          Risk Assessment
      ====================================================== */}

      <section
        className="
          mt-4
          rounded-xl
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-bg)]
          p-4
        "
      >
        <div className="mb-4 flex items-center gap-2">
          <ShieldAlert size={17} />

          <h3 className="font-semibold">
            Risk Assessment
          </h3>
        </div>

        <div
          className={`
            rounded-lg
            border
            p-4
            ${riskClass}
          `}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm">
              Network Risk
            </span>

            <span className="font-bold">
              {riskLevel}
            </span>
          </div>

          <div className="mt-3">
            <div className="flex items-center justify-between">
              <span className="text-xs opacity-75">
                Adjusted Resilience Index
              </span>

              <span className="font-mono font-semibold">
                {risk.ari.toFixed(3)}
              </span>
            </div>

            <div className="mt-2 h-2 overflow-hidden rounded-full bg-black/20">
              <div
                className="h-full rounded-full bg-current"
                style={{
                  width: `${Math.max(
                    0,
                    Math.min(
                      risk.ari * 100,
                      100
                    )
                  )}%`,
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          Simulation
      ====================================================== */}

      {simulation && (
        <section
          className="
            mt-4
            rounded-xl
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-4
          "
        >
          <div className="mb-4 flex items-center gap-2">
            <AlertTriangle size={17} />

            <h3 className="font-semibold">
              Simulation Impact
            </h3>
          </div>

          <div className="space-y-3">
            <ReportRow
              label="Scenario"
              value={formatScenario(
                simulation.scenario
              )}
            />

            <ReportRow
              label="Removed Nodes"
              value={
                simulation
                  .removed_nodes
                  .length
              }
            />

            <ReportRow
              label="Removed Edges"
              value={
                simulation
                  .removed_edges
                  .length
              }
            />

            <ReportRow
              label="Remaining Nodes"
              value={
                simulation.remaining_nodes
              }
            />

            <ReportRow
              label="Remaining Edges"
              value={
                simulation.remaining_edges
              }
            />

            <ReportRow
              label="Connected Components"
              value={
                simulation.connected_components
              }
            />

            <ReportRow
              label="Largest Component"
              value={
                simulation.largest_component
              }
            />

            <ReportRow
              label="Failed Critical Node"
              value={formatCoordinate(
                simulation.critical_node
              )}
            />
          </div>
        </section>
      )}

      {/* =====================================================
          Recommendation
      ====================================================== */}

      <section
        className="
          mt-4
          rounded-xl
          border
          border-blue-500/30
          bg-blue-500/5
          p-4
        "
      >
        <div className="mb-3 flex items-center gap-2">
          <Target
            size={17}
            className="text-blue-400"
          />

          <h3 className="font-semibold">
            Recommendation
          </h3>
        </div>

        <p className="text-sm leading-6 text-[var(--atlas-text-muted)]">
          {recommendation ||
            risk.recommendation ||
            "No recommendation available."}
        </p>
      </section>

      {/* =====================================================
          Export Button
      ====================================================== */}

      <button
        type="button"
        onClick={exportReport}
        disabled={
          !selectedFile || exporting
        }
        className="
          mt-5
          flex
          w-full
          items-center
          justify-center
          gap-2
          rounded-lg
          bg-blue-600
          px-4
          py-3
          font-medium
          text-white
          transition
          hover:bg-blue-700
          active:scale-[0.99]
          disabled:cursor-not-allowed
          disabled:opacity-50
        "
      >
        <FileDown size={18} />

        {exporting
          ? "Generating Report..."
          : "Export PDF Report"}
      </button>

      <p
        className="
          mt-3
          text-center
          text-xs
          text-[var(--atlas-text-muted)]
        "
      >
        Generate a PDF report for the current analysis.
      </p>
    </div>
  );
};

/* =========================================================
   Components
========================================================= */

interface MetricProps {
  label: string;
  value: string | number;
}

const Metric = ({
  label,
  value,
}: MetricProps) => {
  return (
    <div
      className="
        rounded-lg
        border
        border-[var(--atlas-border)]
        p-3
      "
    >
      <p className="text-xs text-[var(--atlas-text-muted)]">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold">
        {value}
      </p>
    </div>
  );
};

interface ReportRowProps {
  label: string;
  value: string | number;
}

const ReportRow = ({
  label,
  value,
}: ReportRowProps) => {
  return (
    <div
      className="
        flex
        items-center
        justify-between
        gap-4
        border-b
        border-[var(--atlas-border)]
        pb-2
        last:border-0
      "
    >
      <span className="text-sm text-[var(--atlas-text-muted)]">
        {label}
      </span>

      <span className="text-right text-sm font-semibold">
        {value}
      </span>
    </div>
  );
};

/* =========================================================
   Formatting
========================================================= */

const formatSize = (
  size: number[]
) => {
  if (size.length >= 2) {
    return `${size[0]} × ${size[1]}`;
  }

  return size.join(" × ");
};

const formatCoordinate = (
  coordinate:
    | [number, number]
    | number[]
    | undefined
) => {
  if (
    !coordinate ||
    coordinate.length < 2
  ) {
    return "—";
  }

  return `(${coordinate[0]}, ${coordinate[1]})`;
};

const formatScenario = (
  scenario: string
) => {
  return scenario
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
};

export default ReportPanel;