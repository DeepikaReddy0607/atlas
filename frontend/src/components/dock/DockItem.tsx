interface DockItemProps {
  icon: React.ComponentType<{
    size?: number;
    strokeWidth?: number;
  }>;

  label: string;

  active?: boolean;

  onClick?: () => void;
}

const DockItem = ({
  icon: Icon,
  label,
  active = false,
  onClick,
}: DockItemProps) => {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-current={active ? "page" : undefined}
      className={`
        group
        relative
        flex
        h-[86px]
        w-full
        flex-col
        items-center
        justify-center
        gap-[7px]
        border-b
        border-[#0C2115]
        transition-all
        duration-200

        ${
          active
            ? `
              bg-[#07150D]
              text-[#8BFF3D]
            `
            : `
              text-[#52665A]
              hover:bg-[#06110B]
              hover:text-[#A0B3A4]
            `
        }
      `}
    >

      {/* =================================================
          ACTIVE INDICATOR
      ================================================= */}

      <span
        className={`
          absolute
          left-0
          top-0
          h-full
          w-[3px]
          bg-[#8BFF3D]
          shadow-[0_0_12px_rgba(139,255,61,0.55)]
          transition-opacity
          duration-200

          ${
            active
              ? "opacity-100"
              : "opacity-0"
          }
        `}
      />

      {/* =================================================
          ICON
      ================================================= */}

      <Icon
        size={21}
        strokeWidth={1.5}
      />

      {/* =================================================
          LABEL
      ================================================= */}

      <span
        className="
          max-w-[76px]
          px-1
          text-center
          font-mono
          text-[8px]
          font-medium
          uppercase
          leading-[1.2]
          tracking-[0.12em]
        "
      >
        {label}
      </span>

      {/* =================================================
          ACTIVE DOT
      ================================================= */}

      {active && (
        <span
          className="
            absolute
            bottom-[9px]
            h-[3px]
            w-[3px]
            rounded-full
            bg-[#8BFF3D]
            shadow-[0_0_7px_rgba(139,255,61,0.8)]
          "
        />
      )}
    </button>
  );
};

export default DockItem;