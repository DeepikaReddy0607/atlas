import {
  Activity,
  FileText,
  Layers,
  Maximize2,
  Play,
  RotateCcw,
  Search,
  Upload,
  X,
} from "lucide-react";
import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  onNewAnalysis: () => void;
  onRunAnalysis?: ()=> void;
  onResetView?: () => void;
  onFullscreen?: () => void;
  onRunSimulation?: () => void;
  onGenerateReport?: () => void;
}

interface Command {
  id: string;
  label: string;
  description: string;
  icon: typeof Search;
  action: () => void;
}

const CommandPalette = ({
  open,
  onClose,
  onNewAnalysis,
  onRunAnalysis,
  onResetView,
  onFullscreen,
  onRunSimulation,
  onGenerateReport,
}: CommandPaletteProps) => {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] =
    useState(0);

  const inputRef =
    useRef<HTMLInputElement | null>(null);

  // =========================================================
  // COMMANDS
  // =========================================================

  const commands: Command[] = useMemo(
    () => [
      {
        id: "new-analysis",
        label: "New Analysis",
        description: "Start a new satellite analysis",
        icon: Upload,
        action: onNewAnalysis,
      },
      {
        id: "run-analysis",
        label: "Run Analysis",
        description: "Process the selected imagery",
        icon: Play,
        action: ()=>{
          onRunAnalysis?.();
          onClose();
        },
      },
      {
        id: "layers",
        label: "Toggle Layers",
        description: "Open the analysis layer controls",
        icon: Layers,
        action: () => {
          onClose();
        },
      },
      {
        id: "simulation",
        label: "Run Simulation",
        description: "Execute the selected failure scenario",
        icon: Activity,
        action: () => {
          onRunSimulation?.();
          onClose();
        },
      },
      {
        id: "report",
        label: "Generate Report",
        description: "Generate the ATLAS analysis report",
        icon: FileText,
        action: () => {
          onGenerateReport?.();
          onClose();
        },
      },
      {
        id: "reset-view",
        label: "Reset View",
        description: "Reset zoom and map position",
        icon: RotateCcw,
        action: () => {
          onResetView?.();
          onClose();
        },
      },
      {
        id: "fullscreen",
        label: "Fullscreen",
        description: "Toggle fullscreen workspace",
        icon: Maximize2,
        action: () => {
          onFullscreen?.();
          onClose();
        },
      },
    ],
    [
      onNewAnalysis,
      onClose,
      onResetView,
      onFullscreen,
      onRunSimulation,
      onGenerateReport,
    ]
  );

  // =========================================================
  // FILTER
  // =========================================================

  const filteredCommands = commands.filter(
    (command) =>
      command.label
        .toLowerCase()
        .includes(query.toLowerCase()) ||
      command.description
        .toLowerCase()
        .includes(query.toLowerCase())
  );

  // =========================================================
  // OPEN / CLOSE
  // =========================================================

  useEffect(() => {
    if (!open) {
      return;
    }

    setQuery("");
    setSelectedIndex(0);

    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  }, [open]);

  // =========================================================
  // KEYBOARD
  // =========================================================

  useEffect(() => {
    if (!open) {
      return;
    }

    const handleKeyDown = (
      event: KeyboardEvent
    ) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key === "ArrowDown") {
        event.preventDefault();

        setSelectedIndex((current) =>
          Math.min(
            current + 1,
            filteredCommands.length - 1
          )
        );

        return;
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();

        setSelectedIndex((current) =>
          Math.max(current - 1, 0)
        );

        return;
      }

      if (
        event.key === "Enter" &&
        filteredCommands.length > 0
      ) {
        event.preventDefault();

        filteredCommands[selectedIndex]?.action();
      }
    };

    window.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, [
    open,
    onClose,
    filteredCommands,
    selectedIndex,
  ]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/40 pt-[14vh] backdrop-blur-[2px]"
      onMouseDown={(event) => {
        if (
          event.target === event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <div
        className="
          w-[560px]
          overflow-hidden
          rounded-xl
          border
          border-[#21452E]
          bg-[#06110B]
          shadow-2xl
        "
      >
        {/* =================================================
            SEARCH
        ================================================= */}

        <div
          className="
            flex
            items-center
            gap-3
            border-b
            border-[#183522]
            px-4
          "
        >
          <Search
            size={18}
            className="shrink-0 text-[#718578]"
          />

          <input
            ref={inputRef}
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Search ATLAS commands..."
            className="
              h-14
              flex-1
              bg-transparent
              text-sm
              text-[#E8F0E8]
              outline-none
              placeholder:text-[#52655A]
            "
          />

          <button
            type="button"
            onClick={onClose}
            className="
              rounded
              p-1
              text-[#718578]
              hover:bg-[#102319]
              hover:text-[#E8F0E8]
            "
            aria-label="Close command palette"
          >
            <X size={16} />
          </button>
        </div>

        {/* =================================================
            COMMANDS
        ================================================= */}

        <div className="max-h-[420px] overflow-y-auto p-2">

          {filteredCommands.length === 0 ? (
            <div
              className="
                px-4
                py-10
                text-center
                text-sm
                text-[#718578]
              "
            >
              No commands found.
            </div>
          ) : (
            filteredCommands.map(
              (command, index) => {
                const Icon = command.icon;

                const selected =
                  index === selectedIndex;

                return (
                  <button
                    key={command.id}
                    type="button"
                    className={`
                      flex
                      w-full
                      items-center
                      gap-3
                      rounded-lg
                      px-3
                      py-3
                      text-left
                      transition
                      ${
                        selected
                          ? "bg-[#12301D] text-[#E8F0E8]"
                          : "text-[#A9B7AC] hover:bg-[#0C1D12]"
                      }
                    `}
                    onMouseEnter={() =>
                      setSelectedIndex(index)
                    }
                    onClick={command.action}
                  >
                    <div
                      className="
                        flex
                        h-8
                        w-8
                        shrink-0
                        items-center
                        justify-center
                        rounded-md
                        border
                        border-[#21452E]
                        bg-[#08170D]
                      "
                    >
                      <Icon size={16} />
                    </div>

                    <div className="min-w-0 flex-1">

                      <div className="text-sm font-medium">
                        {command.label}
                      </div>

                      <div className="mt-0.5 text-xs text-[#617267]">
                        {command.description}
                      </div>

                    </div>

                    {selected && (
                      <kbd
                        className="
                          rounded
                          border
                          border-[#31573D]
                          px-1.5
                          py-0.5
                          text-[10px]
                          text-[#81968A]
                        "
                      >
                        Enter
                      </kbd>
                    )}
                  </button>
                );
              }
            )
          )}

        </div>

        {/* =================================================
            FOOTER
        ================================================= */}

        <div
          className="
            flex
            items-center
            justify-between
            border-t
            border-[#183522]
            px-4
            py-2
            text-[10px]
            uppercase
            tracking-wider
            text-[#52655A]
          "
        >
          <span>ATLAS COMMAND</span>

          <span>
            ↑ ↓ Navigate&nbsp;&nbsp; Enter Select&nbsp;&nbsp; Esc Close
          </span>
        </div>

      </div>
    </div>
  );
};

export default CommandPalette;