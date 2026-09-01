import {
  Plus,
  X,
  FileImage,
} from "lucide-react";

import { useWorkspace } from "../../../context/WorkspaceContext";

const WorkspaceTabs = () => {
  const {
    workspaces,
    activeWorkspaceId,
    setActiveWorkspaceId,
    addWorkspace,
    closeWorkspace,
  } = useWorkspace();

  return (
    <div className="flex min-w-0 items-center gap-1">

      {/* =====================================================
          WORKSPACE TABS
      ===================================================== */}

      <div className="flex min-w-0 items-center gap-1">

        {workspaces.map((workspace) => {
          const active =
            workspace.id ===
            activeWorkspaceId;

          return (
            <button
              key={workspace.id}
              onClick={() =>
                setActiveWorkspaceId(
                  workspace.id
                )
              }
              className={`
                group
                relative
                flex
                h-9
                max-w-56
                min-w-36
                items-center
                gap-2
                rounded-lg
                border
                px-3
                text-sm
                transition-all
                duration-200

                ${
                  active
                    ? `
                      border-[var(--atlas-border)]
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
              {/* Active indicator */}

              {active && (
                <span
                  className="
                    absolute
                    bottom-0
                    left-3
                    right-3
                    h-0.5
                    rounded-full
                    bg-blue-500
                  "
                />
              )}

              <FileImage
                size={14}
                className={
                  active
                    ? "text-blue-400"
                    : "text-[var(--atlas-text-muted)]"
                }
              />

              <span className="min-w-0 flex-1 truncate text-left">
                {workspace.name}
              </span>

              {/* Close */}

              <span
                role="button"
                tabIndex={0}
                onClick={(event) => {
                  event.stopPropagation();
                  closeWorkspace(
                    workspace.id
                  );
                }}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" ||
                    event.key === " "
                  ) {
                    event.preventDefault();
                    event.stopPropagation();

                    closeWorkspace(
                      workspace.id
                    );
                  }
                }}
                className="
                  flex
                  h-5
                  w-5
                  shrink-0
                  items-center
                  justify-center
                  rounded
                  text-[var(--atlas-text-muted)]
                  opacity-0
                  transition-all
                  duration-150
                  hover:bg-white/10
                  hover:text-[var(--atlas-text)]
                  group-hover:opacity-100
                "
              >
                <X size={13} />
              </span>
            </button>
          );
        })}
      </div>

      {/* =====================================================
          NEW WORKSPACE
      ===================================================== */}

      <button
        onClick={addWorkspace}
        title="New workspace"
        className="
          flex
          h-9
          w-9
          shrink-0
          items-center
          justify-center
          rounded-lg
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
      >
        <Plus size={17} />
      </button>
    </div>
  );
};

export default WorkspaceTabs;