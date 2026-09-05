import type { AtlasResult } from "../../types/atlas";

import Section from "./Section";
import Row from "./Row";

interface AnalysisInspectorProps {
  analysis: AtlasResult;
  selectedLayerId: string;
}

const AnalysisInspector = ({
  analysis,
  selectedLayerId,
}: AnalysisInspectorProps) => {
  const simulation = analysis.simulation;

  return (
    <div
      className="
        h-full
        overflow-y-auto
        p-4
      "
    >
      <div
        className="
          mb-6
          rounded-lg
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-surface)]
          p-4
        "
      >
        <h2 className="text-xl font-semibold">
          ATLAS Analysis
        </h2>

        <Section title="Overview">
          <Row
            label="Model"
            value={analysis.segmentation.model_name}
          />

          <Row
            label="Risk"
            value={
              <span
                className={`
                  rounded-full
                  px-2
                  py-0.5
                  text-xs
                  font-semibold
                  ${
                    analysis.risk.level === "HIGH"
                      ? "bg-red-500/20 text-red-400"
                      : analysis.risk.level === "MEDIUM"
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-green-500/20 text-green-400"
                  }
                `}
              >
                {analysis.risk.level}
              </span>
            }
          />

          <Row
            label="ARI"
            value={
              <span className="font-mono">
                {analysis.risk.ari.toFixed(3)}
              </span>
            }
          />

          <Row
            label="Nodes"
            value={analysis.topology_graph.nodes}
          />

          <Row
            label="Edges"
            value={analysis.topology_graph.edges}
          />

          <Row
            label="Scenario"
            value={
              simulation?.scenario ?? "Not Executed"
            }
          />
        </Section>

        <div
          className="
            mb-6
            rounded-lg
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-3
          "
        >
          <p className="text-sm text-[var(--atlas-text-muted)]">
            Active Layer
          </p>

          <h3 className="mt-1 text-lg font-semibold">
            {selectedLayerId.replace("_", " ")}
          </h3>

          <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
            AI-generated road network intelligence
          </p>
        </div>

        {selectedLayerId === "segmentation" && (
          <>
            <Section title="Vision">
              <Row
                label="Model"
                value={analysis.segmentation.model_name}
              />

              <Row
                label="Inference"
                value={`${analysis.segmentation.inference_time_ms.toFixed(2)} ms`}
              />
            </Section>

            <Section title="Image">
              <Row
                label="Image Size"
                value={`${analysis.segmentation.image_size[0]} × ${analysis.segmentation.image_size[1]}`}
              />

              <Row
                label="Mask Size"
                value={`${analysis.segmentation.mask_shape[0]} × ${analysis.segmentation.mask_shape[1]}`}
              />
            </Section>
          </>
        )}

        {selectedLayerId === "road_mask" && (
          <Section title="Road Mask">
            <Row
              label="Source"
              value="Segmentation Output"
            />

            <Row
              label="Status"
              value="Generated"
            />
          </Section>
        )}

        {selectedLayerId === "skeleton" && (
          <Section title="Skeleton">
            <Row
              label="Algorithm"
              value="Skeletonize"
            />

            <Row
              label="Purpose"
              value="Road Centerlines"
            />
          </Section>
        )}

        {selectedLayerId === "graph" && (
          <Section title="Topology Graph">
            <Row
              label="Nodes"
              value={analysis.topology_graph.nodes}
            />

            <Row
              label="Edges"
              value={analysis.topology_graph.edges}
            />
          </Section>
        )}

        {selectedLayerId === "criticality" && (
          <>
            <Section title="Risk">
              <Row
                label="ARI"
                value={
                  <span className="font-mono">
                    {analysis.risk.ari.toFixed(3)}
                  </span>
                }
              />

              <Row
                label="Level"
                value={
                  <span
                    className={`
                      rounded-full
                      px-2
                      py-0.5
                      text-xs
                      font-semibold
                      ${
                        analysis.risk.level === "HIGH"
                          ? "bg-red-500/20 text-red-400"
                          : analysis.risk.level === "MEDIUM"
                          ? "bg-yellow-500/20 text-yellow-400"
                          : "bg-green-500/20 text-green-400"
                      }
                    `}
                  >
                    {analysis.risk.level}
                  </span>
                }
              />
            </Section>

            <Section title="Resilience">
              <Row
                label="Components"
                value={
                  analysis.resilience.connected_components
                }
              />

              <Row
                label="Largest Component"
                value={
                  analysis.resilience.largest_component
                }
              />
            </Section>

            <Section title="Simulation">
              <Row
                label="Scenario"
                value={
                  simulation?.scenario ?? "Not Executed"
                }
              />

              {simulation ? (
                <>
                  <Row
                    label="Removed Nodes"
                    value={simulation.removed_nodes.length}
                  />

                  <Row
                    label="Remaining Nodes"
                    value={simulation.remaining_nodes}
                  />

                  <Row
                    label="Remaining Edges"
                    value={simulation.remaining_edges}
                  />

                  <Row
                    label="Components"
                    value={simulation.connected_components}
                  />

                  <Row
                    label="Largest Component"
                    value={simulation.largest_component}
                  />
                </>
              ) : (
                <Row
                  label="Status"
                  value="Not Executed"
                />
              )}
            </Section>

            <Section title="Recommendation">
              <p
                className="
                  text-sm
                  leading-6
                "
              >
                {analysis.recommendation ??
                  "No recommendation available."}
              </p>
            </Section>
          </>
        )}
      </div>
    </div>
  );
};

export default AnalysisInspector;