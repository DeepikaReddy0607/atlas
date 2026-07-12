import { Search } from "lucide-react";

const SearchBar = () => {
  return (
    <button
      className="
        flex
        h-10
        w-72
        items-center
        justify-between
        rounded-[var(--radius-md)]
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
        px-3
        transition-all
        duration-200
        hover:border-[var(--atlas-primary)]
        hover:bg-[var(--atlas-elevated)]
      "
    >
      <div className="flex items-center gap-2">
        <Search
          size={16}
          className="text-[var(--atlas-text-muted)]"
        />

        <span
          className="
            text-sm
            text-[var(--atlas-text-muted)]
          "
        >
          Search commands...
        </span>
      </div>

      <kbd
        className="
          rounded-md
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-bg)]
          px-2
          py-1
          text-[10px]
          font-medium
          text-[var(--atlas-text-muted)]
        "
      >
        Ctrl K
      </kbd>
    </button>
  );
};

export default SearchBar;