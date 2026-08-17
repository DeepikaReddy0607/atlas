import { useState } from "react";
import type { ReactNode } from "react";
import { toast } from "sonner";

import { analyzeImage } from "../api/atlasApi";
import type { AtlasResult } from "../types/atlas";

import {
  AtlasAnalysisContext,
} from "../context/AtlasAnalysisContext";

interface Props {
  children: ReactNode;
}

const AtlasAnalysisProvider = ({
  children,
}: Props) => {
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [analysisResult, setAnalysisResult] =
    useState<AtlasResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const analyze = async (file: File) => {
    try {
      setSelectedFile(file);
      setLoading(true);
      setError(null);

      toast.loading("Analyzing satellite image...", {
        id: "analysis",
      });

      const result = await analyzeImage(file);

      setAnalysisResult(result);

      toast.success("Analysis completed successfully!", {
        id: "analysis",
      });

    } catch (err) {
      console.error("Provider error:", err);

      setError("Analysis failed.");

      toast.error("Analysis failed.", {
        id: "analysis",
      });

    } finally {
      setLoading(false);
    }
  };

  return (
    <AtlasAnalysisContext.Provider
      value={{
        selectedFile,
        analysisResult,
        loading,
        error,
        analyze,
      }}
    >
      {children}
    </AtlasAnalysisContext.Provider>
  );
};

export default AtlasAnalysisProvider;