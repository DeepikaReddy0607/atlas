import type { AtlasWorkspace } from "../context/WorkspaceContext";
import type { AtlasResult } from "../types/atlas";
import type { Layer } from "../types/layer";

/* ============================================================
   ATLAS Workspace File
============================================================ */

export interface AtlasWorkspaceFile {
  format: "ATLAS_WORKSPACE";
  version: 1;

  workspace: {
    name: string;
    createdAt: number;
  };

  source: {
    fileName: string | null;
  };

  analysisResult: AtlasResult | null;

  layers: Layer[];

  selectedLayerId: string | null;

  savedAt: number;
}

/* ============================================================
   Export Workspace
============================================================ */

export function exportWorkspace(
  workspace: AtlasWorkspace
): void {
  const workspaceFile: AtlasWorkspaceFile = {
    format: "ATLAS_WORKSPACE",

    version: 1,

    workspace: {
      name: workspace.name,
      createdAt: workspace.createdAt,
    },

    source: {
      fileName:
        workspace.selectedFile?.name ?? null,
    },

    analysisResult:
      workspace.analysisResult,

    layers:
      workspace.layers,

    selectedLayerId:
      workspace.selectedLayerId,

    savedAt: Date.now(),
  };

  const json =
    JSON.stringify(
      workspaceFile,
      null,
      2
    );

  const blob =
    new Blob(
      [json],
      {
        type: "application/json",
      }
    );

  const url =
    URL.createObjectURL(blob);

  const anchor =
    document.createElement("a");

  anchor.href = url;

  anchor.download =
    workspace.name.endsWith(".atlas")
      ? workspace.name
      : `${workspace.name}.atlas`;

  document.body.appendChild(anchor);

  anchor.click();

  document.body.removeChild(anchor);

  URL.revokeObjectURL(url);
}