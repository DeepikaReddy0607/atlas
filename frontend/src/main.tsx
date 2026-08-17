import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./styles/index.css";
import App from "./App";

import AtlasAnalysisProvider from "./providers/AtlasAnalysisProvider";
import { SimulationProvider } from "./context/SimulationContext";
import { LayerSelectionProvider } from "./context/LayerSelectionContext";
import { GraphSelectionProvider } from "./context/GraphSelectionContext";
import { DockProvider } from "./context/DockContext";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AtlasAnalysisProvider>
      <SimulationProvider>
        <LayerSelectionProvider>
          <GraphSelectionProvider>
            <DockProvider>
              <App />
            </DockProvider>
          </GraphSelectionProvider>
        </LayerSelectionProvider>
      </SimulationProvider>
    </AtlasAnalysisProvider>
  </StrictMode>
);