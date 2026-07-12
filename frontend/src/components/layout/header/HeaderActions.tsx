import {
  Bell,
  Settings,
  CircleUserRound,
} from "lucide-react";

const HeaderActions = () => {
  return (
    <div className="flex items-center gap-2">

      {/* Notifications */}
      <button
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