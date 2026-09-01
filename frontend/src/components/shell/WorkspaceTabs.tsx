import {
  Plus,
  X,
  FileImage,
} from "lucide-react";

import { useWorkspace } from "../../context/WorkspaceContext";

const WorkspaceTabs = () => {
  const {
    workspaces,
    activeWorkspaceId,
    setActiveWorkspaceId,
    addWorkspace,
    closeWorkspace,
    renameWorkspace,
  } = useWorkspace();

  // ---------------------------------------------------------
  // Create workspace
  // ---------------------------------------------------------

  const handleAddWorkspace = () => {
    addWorkspace();
  };

  // ---------------------------------------------------------
  // Close workspace
  // ---------------------------------------------------------

  const handleCloseWorkspace = (
    event: React.MouseEvent,
    id: string
  ) => {
    event.stopPropagation();

    // WorkspaceContext already prevents
    // closing the final workspace.
    closeWorkspace(id);
  };

  // ---------------------------------------------------------
  // Rename workspace
  // ---------------------------------------------------------

  const handleRenameWorkspace = (
    id: string,
    currentName: string
  ) => {
    const newName = window.prompt(
      "Rename workspace",
      currentName
    );

    if (newName === null) {
      return;
    }

    const trimmedName = newName.trim();

    if (!trimmedName) {
      return;
    }

    renameWorkspace(
      id,
      trimmedName
    );
  };

  return (
    <div
      className="
        flex
        min-w-0
        items-center
        gap-1
      "
    >
      {/* =====================================================
          Workspace Tabs
      ====================================================== */}

      <div
        className="
          flex
          min-w-0
          max-w-[calc(100vw-280px)]
          items-center
          gap-1
          overflow-x-auto
          scrollbar-none
        "
      >
        {workspaces.map((workspace) => {
          const isActive =
            workspace.id === activeWorkspaceId;

          const hasAnalysis =
            workspace.analysisResult !== null;

          return (
            <div
              key={workspace.id}
              onClick={() =>
                setActiveWorkspaceId(
                  workspace.id
                )
              }
              onDoubleClick={() =>
                handleRenameWorkspace(
                  workspace.id,
                  workspace.name
                )
              }
              className={`
                group
                relative
                flex
                h-10
                min-w-[150px]
                max-w-[230px]
                cursor-pointer
                items-center
                gap-2
                rounded-t-[var(--radius-md)]
                border
                px-3
                transition-all
                duration-200
                ease-out

                ${
                  isActive
                    ? `
                      border-[var(--atlas-border)]
                      border-b-transparent
                      bg-[var(--atlas-surface)]
                      text-[var(--atlas-text)]
                      shadow-sm
                    `
                    : `
                      border-transparent
                      bg-transparent
                      text-[var(--atlas-text-muted)]
                      hover:border-[var(--atlas-border)]
                      hover:bg-[var(--atlas-surface)]
                      hover:text-[var(--atlas-text)]
                    `
                }
              `}
            >
              {/* ------------------------------------------------
                  Active indicator
              ------------------------------------------------- */}

              {isActive && (
                <span
                  className="
                    absolute
                    bottom-0
                    left-2
                    right-2
                    h-[2px]
                    rounded-full
                    bg-blue-500
                  "
                />
              )}

              {/* ------------------------------------------------
                  Workspace icon
              ------------------------------------------------- */}

              <FileImage
                size={15}
                className={`
                  shrink-0
                  transition-colors
                  duration-200
                  ${
                    isActive
                      ? "text-blue-400"
                      : "text-[var(--atlas-text-muted)]"
                  }
                `}
              />

              {/* ------------------------------------------------
                  Workspace name
              ------------------------------------------------- */}

              <span
                className="
                  min-w-0
                  flex-1
                  truncate
                  text-sm
                  font-medium
                "
                title={workspace.name}
              >
                {workspace.name}
              </span>

              {/* ------------------------------------------------
                  Analysis indicator
              ------------------------------------------------- */}

              {hasAnalysis && (
                <span
                  className="
                    h-1.5
                    w-1.5
                    shrink-0
                    rounded-full
                    bg-emerald-400
                  "
                  title="Analysis available"
                />
              )}

              {/* ------------------------------------------------
                  Close button
              ------------------------------------------------- */}

              {workspaces.length > 1 && (
                <button
                  type="button"
                  onClick={(event) =>
                    handleCloseWorkspace(
                      event,
                      workspace.id
                    )
                  }
                  className="
                    flex
                    h-6
                    w-6
                    shrink-0
                    items-center
                    justify-center
                    rounded-md
                    text-[var(--atlas-text-muted)]
                    opacity-0
                    transition-all
                    duration-150
                    hover:bg-white/10
                    hover:text-[var(--atlas-text)]
                    group-hover:opacity-100
                  "
                  title="Close workspace"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* =====================================================
          Add Workspace
      ====================================================== */}

      <button
        type="button"
        onClick={handleAddWorkspace}
        className="
          ml-1
          flex
          h-9
          w-9
          shrink-0
          items-center
          justify-center
          rounded-[var(--radius-md)]
          border
          border-transparent
          text-[var(--atlas-text-muted)]
          transition-all
          duration-200
          hover:border-[var(--atlas-border)]
          hover:bg-[var(--atlas-surface)]
          hover:text-[var(--atlas-text)]
          active:scale-95
        "
        title="New workspace"
      >
        <Plus size={18} />
      </button>
    </div>
  );
};

export default WorkspaceTabs;