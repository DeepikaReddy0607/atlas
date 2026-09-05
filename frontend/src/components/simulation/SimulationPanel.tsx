import {
  RotateCcw,
  Activity,
  Network,
  AlertTriangle,
} from "lucide-react";

import { useSimulation } from "../../context/SimulationContext";
import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";

import ScenarioCard from "./ScenarioCard";
import RunSimulationButton from "./RunSimulationButton";
import { runSimulation } from "../../api/simulationApi";

const SimulationPanel = () => {
  const { analysisResult } = useAtlasAnalysis();

  const {
    selectedScenario,
    setSelectedScenario,
    running,
    setRunning,
    result,
    setResult,
    error,
    setError,
  } = useSimulation();

  const topology = analysisResult?.topology_graph;
  const resilience = analysisResult?.resilience;

  /*
   * ---------------------------------------------------------
   * Baseline network
   * ---------------------------------------------------------
   */

  const criticalNode =
    resilience?.critical_node ?? null;

  const originalNodes =
    result?.original_nodes ??
    topology?.nodes ??
    0;

  const originalEdges =
    result?.original_edges ??
    topology?.edges ??
    0;

  /*
   * ---------------------------------------------------------
   * Simulated network
   * ---------------------------------------------------------
   */

  const remainingNodes =
    result?.remaining_nodes ?? 0;

  const remainingEdges =
    result?.remaining_edges ?? 0;

  const componentCount =
    result?.connected_components ?? 0;

  const largestComponent =
    result?.largest_component ?? 0;

  /*
   * ---------------------------------------------------------
   * Impact calculations
   * ---------------------------------------------------------
   */

  const nodeLossPercent =
    originalNodes > 0
      ? ((originalNodes - remainingNodes) /
          originalNodes) *
        100
      : 0;

  const edgeLossPercent =
    originalEdges > 0
      ? ((originalEdges - remainingEdges) /
          originalEdges) *
        100
      : 0;

  /*
   * ---------------------------------------------------------
   * Network status
   * ---------------------------------------------------------
   */

  const networkStatus =
    analysisResult?.risk?.level ??
    "UNKNOWN";

  const networkAvailable =
    !!analysisResult;

  /*
   * ---------------------------------------------------------
   * Run simulation
   * ---------------------------------------------------------
   */

  const handleRunSimulation = async () => {
    if (!analysisResult || running) {
      return;
    }

    setRunning(true);
    setError(null);
    setResult(null);

    try {
      const simulationResult =
        await runSimulation(
          selectedScenario,
          selectedScenario === "node"
            ? criticalNode ?? undefined
            : undefined
        );
        setResult(simulationResult);
    } catch (err) {
      console.error(
        "Simulation request failed:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Simulation failed. Please check the backend."
      );
    } finally {
      setRunning(false);
    }
  };

  /*
   * ---------------------------------------------------------
   * Reset
   * ---------------------------------------------------------
   */

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div
      className="
        h-full
        overflow-y-auto
        p-4
      "
    >
      {/* =====================================================
          HEADER
      ====================================================== */}

      <div className="flex items-start gap-3">
        <div
          className="
            rounded-lg
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-2
          "
        >
          <Activity size={18} />
        </div>

        <div>
          <h2 className="text-lg font-semibold">
            Simulation
          </h2>

          <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
            Evaluate network behavior under infrastructure failure.
          </p>
        </div>
      </div>

      {/* =====================================================
          NO ANALYSIS
      ====================================================== */}

      {!networkAvailable && (
        <div
          className="
            mt-6
            rounded-lg
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-4
          "
        >
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} />

            <span className="font-medium">
              Analysis required
            </span>
          </div>

          <p className="mt-2 text-sm text-[var(--atlas-text-muted)]">
            Upload and analyze a satellite image
            before running a network simulation.
          </p>
        </div>
      )}

      {networkAvailable && (
        <>
          {/* =================================================
              CURRENT NETWORK
          ================================================== */}

          <section className="mt-6">
            <div className="mb-3 flex items-center gap-2">
              <Network size={15} />

              <span
                className="
                  text-xs
                  font-medium
                  uppercase
                  tracking-wide
                  text-[var(--atlas-text-muted)]
                "
              >
                Current Network
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Metric
                label="Nodes"
                value={topology?.nodes ?? 0}
              />

              <Metric
                label="Edges"
                value={topology?.edges ?? 0}
              />

              <Metric
                label="Components"
                value={
                  resilience?.connected_components ??
                  0
                }
              />

              <Metric
                label="Largest Component"
                value={
                  resilience?.largest_component ??
                  0
                }
              />
            </div>

            <div
              className="
                mt-2
                rounded-lg
                border
                border-[var(--atlas-border)]
                bg-[var(--atlas-bg)]
                p-3
              "
            >
              <p className="text-xs text-[var(--atlas-text-muted)]">
                Most Critical Node
              </p>

              <p className="mt-1 font-semibold">
                {criticalNode
                  ? `(${criticalNode[0]}, ${criticalNode[1]})`
                  : "—"}
              </p>
            </div>
          </section>

          {/* =================================================
              SCENARIO SELECTION
          ================================================== */}

          {!result && !running && (
            <section className="mt-6">
              <div className="mb-3">
                <span
                  className="
                    text-xs
                    font-medium
                    uppercase
                    tracking-wide
                    text-[var(--atlas-text-muted)]
                  "
                >
                  Failure Scenario
                </span>
              </div>

              <div className="space-y-3">
                <ScenarioCard
                  title="Flood Impact"
                  subtitle="Critical Node Failure"
                  description="Simulate the loss of a critical junction representing a flood-affected road segment and evaluate the resulting connectivity loss."
                  scenario="critical_node"
                  selected={selectedScenario === "critical_node"}
                  onClick={() => setSelectedScenario("critical_node")}
                />

                <ScenarioCard
                  title="Earthquake Impact"
                  subtitle="Critical Edge Failure"
                  description="Simulate the loss of a critical road connection representing earthquake-related infrastructure disruption."
                  scenario="critical_edge"
                  selected={selectedScenario === "critical_edge"}
                  onClick={() => setSelectedScenario("critical_edge")}
                />

                <ScenarioCard
                  title="Bridge Failure"
                  subtitle="Selected Edge Failure"
                  description="Simulate failure of a selected road connection, such as a bridge, and measure the resulting network fragmentation."
                  scenario="edge"
                  selected={selectedScenario === "edge"}
                  onClick={() => setSelectedScenario("edge")}
                />

                <ScenarioCard
                  title="Critical Junction"
                  subtitle="Selected Node Failure"
                  description="Simulate failure of a specific network junction and evaluate the resulting connectivity impact."
                  scenario="node"
                  selected={selectedScenario === "node"}
                  onClick={() => setSelectedScenario("node")}
                />
              </div>
            </section>
          )}

          {/* =================================================
              RUNNING
          ================================================== */}

          {running && (
            <section className="mt-6">
              <div
                className="
                  rounded-lg
                  border
                  border-[var(--atlas-border)]
                  bg-[var(--atlas-bg)]
                  p-5
                "
              >
                <div className="flex items-center gap-3">
                  <div
                    className="
                      h-3
                      w-3
                      animate-pulse
                      rounded-full
                      bg-blue-500
                    "
                  />

                  <span className="font-medium">
                    Running simulation...
                  </span>
                </div>

                <p className="mt-3 text-sm text-[var(--atlas-text-muted)]">
                  Applying the selected failure
                  scenario and recalculating
                  network connectivity.
                </p>
              </div>
            </section>
          )}

          {/* =================================================
              RESULTS
          ================================================== */}

          {result && !running && (
            <section className="mt-6">
              <div className="mb-3 flex items-center justify-between">
                <span
                  className="
                    text-xs
                    font-medium
                    uppercase
                    tracking-wide
                    text-[var(--atlas-text-muted)]
                  "
                >
                  Simulation Result
                </span>

                <span
                  className="
                    rounded-full
                    bg-blue-500/10
                    px-2
                    py-1
                    text-xs
                    text-blue-400
                  "
                >
                  {result.scenario}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <Metric
                  label="Remaining Nodes"
                  value={result.remaining_nodes}
                />

                <Metric
                  label="Remaining Edges"
                  value={result.remaining_edges}
                />

                <Metric
                  label="Components"
                  value={result.connected_components}
                />

                <Metric
                  label="Largest Component"
                  value={result.largest_component}
                />
              </div>

              {/* =================================================
                  NETWORK IMPACT
              ================================================== */}

              <div
                className="
                  mt-3
                  rounded-lg
                  border
                  border-[var(--atlas-border)]
                  bg-[var(--atlas-bg)]
                  p-4
                "
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">
                    Network Impact
                  </p>

                  <span
                    className={`
                      rounded-full
                      px-2.5
                      py-1
                      text-xs
                      font-medium
                      ${
                        networkStatus === "HIGH"
                          ? "bg-red-500/15 text-red-400"
                          : networkStatus === "MODERATE"
                          ? "bg-amber-500/15 text-amber-400"
                          : networkStatus === "LOW"
                          ? "bg-emerald-500/15 text-emerald-400"
                          : "bg-slate-500/15 text-slate-400"
                      }
                    `}
                  >
                    {networkStatus}
                  </span>
                </div>

                <div className="mt-4 space-y-4">
                  <ImpactComparison
                    label="Nodes"
                    before={originalNodes}
                    after={remainingNodes}
                    percentage={nodeLossPercent}
                  />

                  <ImpactComparison
                    label="Edges"
                    before={originalEdges}
                    after={remainingEdges}
                    percentage={edgeLossPercent}
                  />

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm">
                        Components
                      </p>

                      <p className="text-xs text-[var(--atlas-text-muted)]">
                        Network fragmentation
                      </p>
                    </div>

                    <span className="font-semibold">
                      {componentCount}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm">
                        Largest Component
                      </p>

                      <p className="text-xs text-[var(--atlas-text-muted)]">
                        Connected nodes
                      </p>
                    </div>

                    <span className="font-semibold">
                      {largestComponent}
                    </span>
                  </div>
                </div>
              </div>

              {/* =================================================
                  FAILED NODE
              ================================================== */}

              {result.critical_node && (
                <div
                  className="
                    mt-3
                    rounded-lg
                    border
                    border-[var(--atlas-border)]
                    bg-[var(--atlas-bg)]
                    p-4
                  "
                >
                  <p className="text-xs text-[var(--atlas-text-muted)]">
                    Failed Critical Node
                  </p>

                  <p className="mt-1 font-semibold">
                    ({result.critical_node[0]},{" "}
                    {result.critical_node[1]})
                  </p>
                </div>
              )}

              {/* =================================================
                  RESET
              ================================================== */}

              <button
                type="button"
                onClick={handleReset}
                className="
                  mt-4
                  flex
                  w-full
                  items-center
                  justify-center
                  gap-2
                  rounded-lg
                  border
                  border-[var(--atlas-border)]
                  px-4
                  py-2.5
                  text-sm
                  transition
                  hover:bg-[var(--atlas-bg)]
                "
              >
                <RotateCcw size={16} />

                Reset Simulation
              </button>
            </section>
          )}

          {/* =================================================
              ERROR
          ================================================== */}

          {error && (
            <div
              className="
                mt-4
                rounded-lg
                border
                border-red-500/30
                bg-red-500/10
                p-3
                text-sm
                text-red-400
              "
            >
              {error}
            </div>
          )}

          {/* =================================================
              RUN BUTTON
          ================================================== */}

          {!result && !running && (
            <div className="mt-6">
              <RunSimulationButton
                onClick={handleRunSimulation}
                disabled={
                  !analysisResult ||
                  running
                }
              />
            </div>
          )}
        </>
      )}
    </div>
  );
};

/* ============================================================
   Metric
============================================================ */

interface MetricProps {
  label: string;
  value: number | string;
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
        bg-[var(--atlas-bg)]
        p-3
      "
    >
      <p className="text-xs text-[var(--atlas-text-muted)]">
        {label}
      </p>

      <p className="mt-1 text-lg font-semibold">
        {value}
      </p>
    </div>
  );
};

/* ============================================================
   Impact Comparison
============================================================ */

interface ImpactComparisonProps {
  label: string;
  before: number;
  after: number;
  percentage: number;
}

const ImpactComparison = ({
  label,
  before,
  after,
  percentage,
}: ImpactComparisonProps) => {
  const percentageRemaining =
    before > 0
      ? Math.max(
          0,
          Math.min(
            100,
            (after / before) * 100
          )
        )
      : 0;

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm">
            {label}
          </p>

          <p className="text-xs text-[var(--atlas-text-muted)]">
            Baseline → simulated
          </p>
        </div>

        <div className="text-right">
          <p className="font-semibold">
            {before} → {after}
          </p>

          <p className="text-xs text-red-400">
            −{percentage.toFixed(1)}%
          </p>
        </div>
      </div>

      <div
        className="
          mt-2
          h-1.5
          overflow-hidden
          rounded-full
          bg-[var(--atlas-border)]
        "
      >
        <div
          className="
            h-full
            rounded-full
            bg-blue-500
            transition-all
            duration-500
          "
          style={{
            width: `${percentageRemaining}%`,
          }}
        />
      </div>
    </div>
  );
};

export default SimulationPanel;

