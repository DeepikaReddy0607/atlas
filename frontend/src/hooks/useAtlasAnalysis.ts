import { useContext } from "react";

import {
  AtlasAnalysisContext,
} from "../context/AtlasAnalysisContext";

export const useAtlasAnalysis = () => {
  const context = useContext(AtlasAnalysisContext);

  if (!context) {
    throw new Error(
      "useAtlasAnalysis must be used inside AtlasAnalysisProvider"
    );
  }

  return context;
};