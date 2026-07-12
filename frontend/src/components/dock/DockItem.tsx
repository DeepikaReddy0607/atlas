import type { LucideIcon } from "lucide-react";

interface DockItemProps {
  icon: LucideIcon;
  label: string;
  active?: boolean;
}

const DockItem = ({
  icon: Icon,
  label,
  active = false,
}: DockItemProps) => {
  return (
    <button
      title={label}
      className={`
        group
        flex
        h-12
        w-12
        items-center
        justify-center
        rounded-md
        transition-all
        duration-200

        ${
          active
            ? "bg-[var(--atlas-primary)] text-white"
            : "text-[var(--atlas-text-muted)] hover:bg-[var(--atlas-surface)] hover:text-[var(--atlas-text)]"
        }
      `}
    >
      <Icon size={20} />
    </button>
  );
};

export default DockItem;