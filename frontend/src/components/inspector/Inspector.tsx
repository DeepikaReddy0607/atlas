import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import { useLayerSelection } from "../../context/LayerSelectionContext";
import { useDock } from "../../context/DockContext";

import EmptyInspector from "./EmptyInspector";
import AnalysisInspector from "./AnalysisInspector";
import ReportPanel from "./ReportPanel";
import ImageInformationPanel from "./ImageInformationPanel";
import TopologyPanel from "./TopologyPanel";
import SimulationPanel from "../simulation/SimulationPanel";
import RiskPanel from "./RiskPanel";
import MapLayersPanel from "./MapLayersPanel";
import SettingsPanel from "./SettingsPanel";
// Temporary panels

const Inspector = () => {
  const { analysisResult } = useAtlasAnalysis();
  const { selectedLayerId } = useLayerSelection();
  const { activeTab } = useDock();

  const renderPanel = () => {
    switch (activeTab) {
      case "imagery":
        return <ImageInformationPanel/>;

      case "ai":
        return analysisResult ? (
          <AnalysisInspector
            analysis={analysisResult}
            selectedLayerId={selectedLayerId}
          />
        ) : (
          <EmptyInspector />
        );

      case "graph":
        return <TopologyPanel />;

      case "map":
        return <MapLayersPanel />;
      
        case "risk":
          return <RiskPanel />
      case "simulation":
        return <SimulationPanel />;

      case "report":
        return <ReportPanel />;

      case "settings":
        return <SettingsPanel />;

      default:
        return <EmptyInspector />;
    }
  };

  return (
    <aside
      className="
      flex
      h-full
      min-h-0
        w-[var(--inspector-width)]
        flex-col
        overflow-hidden
        border-l
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
      "
    >
      {renderPanel()}
    </aside>
  );
};

export default Inspector;