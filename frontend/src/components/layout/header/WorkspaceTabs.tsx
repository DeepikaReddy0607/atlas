import { Plus, X } from "lucide-react";

const WorkspaceTabs = () => {
  return (
    <div className="flex items-center gap-2">

      {/* Active Workspace */}
      <button
        className="
          group
          flex
          h-10
          items-center
          gap-3
          rounded-[var(--radius-md)]
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-surface)]
          px-4
          text-sm
          font-medium
          text-[var(--atlas-text)]
          transition-all
          duration-200
          hover:bg-[var(--atlas-elevated)]
        "
      >
        <span>Untitled.atlas</span>

        <X
          size={14}
          className="
            text-[var(--atlas-text-muted)]
            opacity-0
            transition-opacity
            duration-200
            group-hover:opacity-100
          "
        />
      </button>

      {/* New Workspace */}
      <button
        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-[var(--radius-md)]
          border
          border-[var(--atlas-border)]
          bg-transparent
          text-[var(--atlas-text-muted)]
          transition-all
          duration-200
          hover:bg-[var(--atlas-surface)]
          hover:text-[var(--atlas-text)]
        "
      >
        <Plus size={18} />
      </button>

    </div>
  );
};

export default WorkspaceTabs;