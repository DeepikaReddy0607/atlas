import type { Layer } from "../types/layer";
import {
  createContext,
  useContext,
  useMemo,
  useState,
  useCallback,
  type ReactNode,
} from "react";

import type { AtlasResult } from "../types/atlas";

/* ============================================================
   Workspace Model
============================================================ */

export interface AtlasWorkspace {
  id: string;
  name: string;
  createdAt: number;

  // ----------------------------------------------------------
  // Analysis state
  // ----------------------------------------------------------

  selectedFile: File | null;

  analysisResult: AtlasResult | null;

  loading: boolean;

  error: string | null;
  layers: Layer[];
  selectedLayerId: string | null;
}

/* ============================================================
   Context
============================================================ */

interface WorkspaceContextType {
  workspaces: AtlasWorkspace[];

  activeWorkspaceId: string;

  activeWorkspace: AtlasWorkspace;

  setActiveWorkspaceId: (id: string) => void;

  addWorkspace: () => void;

  closeWorkspace: (id: string) => void;

  renameWorkspace: (
    id: string,
    name: string
  ) => void;

  updateWorkspace: (
    id: string,
    updates: Partial<AtlasWorkspace>
  ) => void;
}

const WorkspaceContext =
  createContext<WorkspaceContextType | null>(null);

/* ============================================================
   Workspace Factory
============================================================ */

const createWorkspace = (
  index = 1
): AtlasWorkspace => {
  return {
    id: crypto.randomUUID(),

    name:
      index === 1
        ? "Untitled.atlas"
        : `Untitled ${index}.atlas`,

    createdAt: Date.now(),

    // --------------------------------------------------------
    // Initial analysis state
    // --------------------------------------------------------

    selectedFile: null,

    analysisResult: null,

    loading: false,

    error: null,

    layers: [],

    selectedLayerId: null,
  };
};

/* ============================================================
   Provider
============================================================ */

export const WorkspaceProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const initialWorkspace =
    createWorkspace(1);

  const [workspaces, setWorkspaces] =
    useState<AtlasWorkspace[]>([
      initialWorkspace,
    ]);

  const [activeWorkspaceId, setActiveWorkspaceId] =
    useState<string>(
      initialWorkspace.id
    );

  /* ==========================================================
     Active Workspace
  ========================================================== */

  const activeWorkspace =
    workspaces.find(
      (workspace) =>
        workspace.id === activeWorkspaceId
    ) ?? workspaces[0];

  /* ==========================================================
     Add Workspace
  ========================================================== */

  const addWorkspace = () => {
    const newWorkspace =
      createWorkspace(
        workspaces.length + 1
      );

    setWorkspaces((prev) => [
      ...prev,
      newWorkspace,
    ]);

    setActiveWorkspaceId(
      newWorkspace.id
    );
  };

  /* ==========================================================
     Close Workspace
  ========================================================== */

  const closeWorkspace = (
    id: string
  ) => {
    setWorkspaces((prev) => {
      // ------------------------------------------------------
      // Never allow the application to have zero workspaces.
      // ------------------------------------------------------

      if (prev.length === 1) {
        return prev;
      }

      const index =
        prev.findIndex(
          (workspace) =>
            workspace.id === id
        );

      const next =
        prev.filter(
          (workspace) =>
            workspace.id !== id
        );

      // ------------------------------------------------------
      // If the active workspace is being closed,
      // activate the nearest remaining workspace.
      // ------------------------------------------------------

      if (
        id === activeWorkspaceId &&
        next.length > 0
      ) {
        const nextIndex =
          Math.max(
            0,
            Math.min(
              index - 1,
              next.length - 1
            )
          );

        setActiveWorkspaceId(
          next[nextIndex].id
        );
      }

      return next;
    });
  };

  /* ==========================================================
     Rename Workspace
  ========================================================== */

  const renameWorkspace = (
    id: string,
    name: string
  ) => {
    setWorkspaces((prev) =>
      prev.map((workspace) =>
        workspace.id === id
          ? {
              ...workspace,
              name,
            }
          : workspace
      )
    );
  };

  /* ==========================================================
     Update Workspace
  ========================================================== */

  const updateWorkspace = useCallback(
  (
    id: string,
    updates: Partial<AtlasWorkspace>
  ) => {
    setWorkspaces((prev) =>
      prev.map((workspace) =>
        workspace.id === id
          ? {
              ...workspace,
              ...updates,
            }
          : workspace
      )
    );
  },
  []
);
  /* ==========================================================
     Context Value
  ========================================================== */

  const value =
    useMemo<WorkspaceContextType>(
      () => ({
        workspaces,

        activeWorkspaceId,

        activeWorkspace,

        setActiveWorkspaceId,

        addWorkspace,

        closeWorkspace,

        renameWorkspace,

        updateWorkspace,
      }),
      [
        workspaces,
        activeWorkspaceId,
        activeWorkspace,
      ]
    );

  /* ==========================================================
     Render
  ========================================================== */

  return (
    <WorkspaceContext.Provider
      value={value}
    >
      {children}
    </WorkspaceContext.Provider>
  );
};

/* ============================================================
   Hook
============================================================ */

export const useWorkspace = () => {
  const context =
    useContext(
      WorkspaceContext
    );

  if (!context) {
    throw new Error(
      "useWorkspace must be used inside WorkspaceProvider"
    );
  }

  return context;
};