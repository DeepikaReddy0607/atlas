import { Network } from "lucide-react";
import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import Row from "./Row";

const TopologyPanel = () => {
  const { analysisResult } = useAtlasAnalysis();

  if (!analysisResult) {
    return (
      <div className="p-6 text-center text-[var(--atlas-text-muted)]">
        <Network size={48} className="mx-auto mb-4 opacity-50" />

        <h2 className="text-lg font-semibold">
          No Topology Available
        </h2>

        <p className="mt-2 text-sm">
          Run an analysis to build the road network.
        </p>
      </div>
    );
  }

  const topology = analysisResult.topology_graph;

  return (
    <div className="space-y-6 p-5">

      <div>
        <h2 className="text-xl font-semibold">
          Topology Analysis
        </h2>

        <p className="text-sm text-[var(--atlas-text-muted)]">
          Road network statistics
        </p>
      </div>

      <div className="space-y-3 rounded-lg border border-[var(--atlas-border)] p-4">

        <Row
          label="Nodes"
          value={topology.nodes}
        />

        <Row
          label="Edges"
          value={topology.edges}
        />
        <Row
            label="Critical Nodes"
            value={analysisResult.criticality.node.length}
        />

        <Row
            label="Connected Components"
            value={analysisResult.resilience.connected_components}
        />

        <Row
            label="Largest Component"
            value={analysisResult.resilience.largest_component}
        />

      </div>
    </div>
  );
};

export default TopologyPanel;