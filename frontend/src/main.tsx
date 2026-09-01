import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./styles/index.css";
import App from "./App";

import AtlasAnalysisProvider from "./providers/AtlasAnalysisProvider";
import { SimulationProvider } from "./context/SimulationContext";
import { LayerSelectionProvider } from "./context/LayerSelectionContext";
import { GraphSelectionProvider } from "./context/GraphSelectionContext";
import { DockProvider } from "./context/DockContext";
import { WorkspaceProvider } from "./context/WorkspaceContext";
import { LayerProvider } from "./context/LayerContext";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <WorkspaceProvider>
      <AtlasAnalysisProvider>
        <LayerProvider>
          <LayerSelectionProvider>
            <GraphSelectionProvider>
              <SimulationProvider>
                <DockProvider>
                  <App />
                </DockProvider>
              </SimulationProvider>
            </GraphSelectionProvider>
          </LayerSelectionProvider>
        </LayerProvider>
      </AtlasAnalysisProvider>
    </WorkspaceProvider>
  </StrictMode>
);
