import { createContext, useContext } from "react";
import type { AtlasResult } from "../types/atlas";

export interface AtlasAnalysisContextType {
  selectedFile: File | null;
  analysisResult: AtlasResult | null;
  loading: boolean;
  error: string | null;
  analyze: (file: File) => Promise<void>;
}

export const AtlasAnalysisContext =
  createContext<AtlasAnalysisContextType | null>(null);

export const useAtlasAnalysis = () => {
  const context = useContext(AtlasAnalysisContext);

  if (!context) {
    throw new Error(
      "useAtlasAnalysis must be used inside AtlasAnalysisProvider"
    );
  }

  return context;
};