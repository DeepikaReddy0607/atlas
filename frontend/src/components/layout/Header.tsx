import {
  Bell,
  Search,
  UserCircle2,
  Plus,
} from "lucide-react";

const Header = () => {
  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-900 px-6">

      {/* ---------- Left Section ---------- */}
      <div className="flex items-center gap-10">

        {/* Brand */}
        <div className="flex flex-col">
          <h1 className="text-lg font-bold tracking-wide text-slate-100">
            ATLAS
          </h1>

          <span className="text-xs text-slate-400">
            Professional Geospatial Analysis Workstation
          </span>
        </div>

        {/* Workspace Tabs */}
        <div className="flex items-center gap-2">

          <button
            className="
              rounded-md
              border
              border-slate-700
              bg-slate-800
              px-4
              py-2
              text-sm
              text-slate-100
              transition-colors
              hover:bg-slate-700
            "
          >
            Untitled.atlas
          </button>

          <button
            className="
              rounded-md
              border
              border-slate-700
              p-2
              text-slate-400
              transition-colors
              hover:bg-slate-800
              hover:text-slate-100
            "
          >
            <Plus size={18} />
          </button>

        </div>

      </div>

      {/* ---------- Right Section ---------- */}
      <div className="flex items-center gap-3">

        {/* Search */}
        <button
          className="
            flex
            items-center
            gap-2
            rounded-md
            border
            border-slate-700
            bg-slate-800
            px-3
            py-2
            text-sm
            text-slate-400
            transition-colors
            hover:bg-slate-700
          "
        >
          <Search size={16} />

          <span>Search</span>

          <kbd
            className="
              rounded
              border
              border-slate-600
              bg-slate-900
              px-2
              py-0.5
              text-[10px]
            "
          >
            Ctrl K
          </kbd>

        </button>

        {/* Notifications */}
        <button
          className="
            rounded-md
            p-2
            text-slate-400
            transition-colors
            hover:bg-slate-800
            hover:text-slate-100
          "
        >
          <Bell size={20} />
        </button>

        {/* Profile */}
        <button
          className="
            flex
            items-center
            gap-2
            rounded-md
            border
            border-slate-700
            bg-slate-800
            px-3
            py-2
            transition-colors
            hover:bg-slate-700
          "
        >
          <UserCircle2
            size={22}
            className="text-slate-300"
          />

          <span className="text-sm text-slate-100">
            Guest
          </span>

        </button>

      </div>

    </header>
  );
};

export default Header;