import type { AtlasResult } from "./atlas";
import type { Layer } from "./layer";

export interface AtlasWorkspace {
  id: string;
  name: string;

  selectedFile: File | null;
  analysisResult: AtlasResult | null;

  layers: Layer[];

  selectedLayerId: string | null;
  selectedNodeId: number | null;

  simulationResult: AtlasResult["simulation"] | null;

  loading: boolean;
  error: string | null;
}