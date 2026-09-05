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

/* ============================================================
   Constants
============================================================ */

const STORAGE_KEY = "atlas-workspaces-v1";

/* ============================================================
   Context
============================================================ */

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

    selectedFile: null,

    analysisResult: null,

    loading: false,

    error: null,

    layers: [],

    selectedLayerId: null,
  };
};

/* ============================================================
   Load Saved Workspaces
============================================================ */

const loadWorkspaces = (): AtlasWorkspace[] => {
  try {
    const stored =
      localStorage.getItem(STORAGE_KEY);

    if (!stored) {
      return [createWorkspace(1)];
    }

    const parsed =
      JSON.parse(stored) as AtlasWorkspace[];

    if (
      !Array.isArray(parsed) ||
      parsed.length === 0
    ) {
      return [createWorkspace(1)];
    }

    /*
     * File objects cannot be restored from JSON.
     * We intentionally restore everything else.
     */
    return parsed.map((workspace) => ({
      ...workspace,
      selectedFile: null,
      loading: false,
    }));
  } catch (error) {
    console.error(
      "Failed to restore ATLAS workspaces:",
      error
    );

    return [createWorkspace(1)];
  }
};

/* ============================================================
   Provider
============================================================ */

export const WorkspaceProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [workspaces, setWorkspaces] =
    useState<AtlasWorkspace[]>(
      loadWorkspaces
    );

  const [activeWorkspaceId, setActiveWorkspaceId] =
    useState<string>(
      () => workspaces[0]?.id
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
     Persist Workspaces
  ========================================================== */

  const persistWorkspaces = useCallback(
    (next: AtlasWorkspace[]) => {
      try {
        /*
         * Do not attempt to serialize File objects.
         */
        const serializable =
          next.map((workspace) => ({
            ...workspace,
            selectedFile: null,
            loading: false,
          }));

        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify(serializable)
        );
      } catch (error) {
        console.error(
          "Failed to persist ATLAS workspace:",
          error
        );
      }
    },
    []
  );

  /* ==========================================================
     Add Workspace
  ========================================================== */

  const addWorkspace = useCallback(() => {
    setWorkspaces((prev) => {
      const newWorkspace =
        createWorkspace(prev.length + 1);

      const next = [
        ...prev,
        newWorkspace,
      ];

      persistWorkspaces(next);

      setActiveWorkspaceId(
        newWorkspace.id
      );

      return next;
    });
  }, [persistWorkspaces]);

  /* ==========================================================
     Close Workspace
  ========================================================== */

  const closeWorkspace = useCallback(
    (id: string) => {
      setWorkspaces((prev) => {
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

        persistWorkspaces(next);

        return next;
      });
    },
    [
      activeWorkspaceId,
      persistWorkspaces,
    ]
  );

  /* ==========================================================
     Rename Workspace
  ========================================================== */

  const renameWorkspace = useCallback(
    (
      id: string,
      name: string
    ) => {
      const cleanName =
        name.trim();

      if (!cleanName) {
        return;
      }

      setWorkspaces((prev) => {
        const next =
          prev.map((workspace) =>
            workspace.id === id
              ? {
                  ...workspace,
                  name:
                    cleanName.endsWith(
                      ".atlas"
                    )
                      ? cleanName
                      : `${cleanName}.atlas`,
                }
              : workspace
          );

        persistWorkspaces(next);

        return next;
      });
    },
    [persistWorkspaces]
  );

  /* ==========================================================
     Update Workspace
  ========================================================== */

  const updateWorkspace = useCallback(
    (
      id: string,
      updates: Partial<AtlasWorkspace>
    ) => {
      setWorkspaces((prev) => {
        const next =
          prev.map((workspace) =>
            workspace.id === id
              ? {
                  ...workspace,
                  ...updates,
                }
              : workspace
          );

        persistWorkspaces(next);

        return next;
      });
    },
    [persistWorkspaces]
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
        addWorkspace,
        closeWorkspace,
        renameWorkspace,
        updateWorkspace,
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