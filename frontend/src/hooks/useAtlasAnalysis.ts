import { useState } from "react";
import { analyzeImage } from "../api/atlasApi";
import type { AtlasResult } from "../types/atlas";

export const useAtlasAnalysis = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [analysisResult, setAnalysisResult] = useState<AtlasResult | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const analyze = async (file: File) => {
    try {
      setSelectedFile(file);

      setLoading(true);

      setError(null);

      const result = await analyzeImage(file);

      console.log("ATLAS RESPONSE");

      console.log(JSON.stringify(result, null, 2));
      
      setAnalysisResult(result);
    } catch (err) {
      console.error(err);

      setError("Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return {
    selectedFile,

    analysisResult,

    loading,

    error,

    analyze,
  };
};