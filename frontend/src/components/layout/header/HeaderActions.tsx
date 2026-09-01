import {
  Bell,
  Settings,
  CircleUserRound,
  Plus,
} from "lucide-react";

import { useDock } from "../../../context/DockContext";

interface HeaderActionsProps {
  onNewAnalysis: () => void;
}

const HeaderActions = ({
  onNewAnalysis,
}: HeaderActionsProps) => {
  const { setActiveTab } = useDock();

  const openSettings = () => {
    setActiveTab("settings");
  };

  return (
    <div className="flex items-center gap-2">

      {/* New Analysis */}

      <button
        type="button"
        onClick={onNewAnalysis}
        className="
          flex
          h-9
          items-center
          gap-2
          rounded-[var(--radius-md)]
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-surface)]
          px-3
          text-xs
          font-semibold
          uppercase
          tracking-[0.08em]
          text-[var(--atlas-text-secondary)]
          transition-all
          duration-200
          hover:border-[var(--atlas-primary)]
          hover:bg-[var(--atlas-elevated)]
          hover:text-[var(--atlas-text)]
          active:scale-[0.98]
        "
        aria-label="Start new analysis"
      >
        <Plus size={16} />
        <span className="hidden xl:inline">
          New Analysis
        </span>
      </button>

      {/* Notifications */}

      <button
        type="button"
        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-[var(--radius-md)]
          text-[var(--atlas-text-muted)]
          transition-all
          duration-200
          hover:bg-[var(--atlas-surface)]
          hover:text-[var(--atlas-text)]
        "
        aria-label="Notifications"
      >
        <Bell size={18} />
      </button>

      {/* Settings */}

      <button
        type="button"
        onClick={openSettings}
        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-[var(--radius-md)]
          text-[var(--atlas-text-muted)]
          transition-all
          duration-200
          hover:bg-[var(--atlas-surface)]
          hover:text-[var(--atlas-text)]
        "
        aria-label="Settings"
      >
        <Settings size={18} />
      </button>

      {/* User */}

      <button
        type="button"
        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-full
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-surface)]
          transition-all
          duration-200
          hover:border-[var(--atlas-primary)]
          hover:bg-[var(--atlas-elevated)]
        "
        aria-label="Profile"
      >
        <CircleUserRound
          size={22}
          className="text-[var(--atlas-text)]"
        />
      </button>

    </div>
  );
};

export default HeaderActions;