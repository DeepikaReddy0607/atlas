import { useEffect, useState } from "react";

import Header from "../layout/header/Header";
import Dock from "../dock/Dock";
import Workspace from "../workspace/Workspace";
import StatusBar from "../statusbar/StatusBar";
import Inspector from "../inspector/Inspector";
import CommandPalette from "../command/CommandPalette";

import { exportWorkspace } from "../../utils/workspaceFile";
import { useWorkspace } from "../../context/WorkspaceContext";
interface AppShellProps {
  onNewAnalysis: () => void;
}

const AppShell = ({
  onNewAnalysis,
}: AppShellProps) => {
  const { activeWorkspace } = useWorkspace();
  const [commandPaletteOpen, setCommandPaletteOpen] =
    useState(false);
    useEffect(() => {
    const handleShortcut = (
      event: KeyboardEvent
    ) => {
      const modifier =
        event.ctrlKey || event.metaKey;

      /* ========================================================
        SAVE WORKSPACE
      ======================================================== */

      if (
        modifier &&
        event.key.toLowerCase() === "s"
      ) {
        event.preventDefault();

        exportWorkspace(
          activeWorkspace
        );

        return;
      }

      /* ========================================================
        COMMAND PALETTE
      ======================================================== */

      if (
        modifier &&
        event.key.toLowerCase() === "k"
      ) {
        event.preventDefault();

        setCommandPaletteOpen(true);

        return;
      }
    };

    window.addEventListener(
      "keydown",
      handleShortcut
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleShortcut
      );
    };
  }, [activeWorkspace]);

  return (
    <div
      className="
        flex
        h-dvh
        w-full
        flex-col
        overflow-hidden
        bg-[#020906]
        text-[#E8F0E8]
      "
    >
      <Header
        onNewAnalysis={onNewAnalysis}
        onOpenCommandPalette={() =>
          setCommandPaletteOpen(true)
        }
      />

      <div className="flex min-h-0 flex-1">

        <aside
          className="
            w-[88px]
            shrink-0
            border-r
            border-[#183522]
            bg-[#030B07]
          "
        >
          <Dock />
        </aside>

        <section
          className="
            relative
            min-h-0
            min-w-0
            flex-1
            overflow-hidden
            bg-[#020906]
          "
        >
          <Workspace
            onNewAnalysis={onNewAnalysis}
            hasAnalysis={
              activeWorkspace.analysisResult !== null
            }
          />
        </section>

        <Inspector />

      </div>

      <StatusBar />

      <CommandPalette
        open={commandPaletteOpen}
        onClose={() =>
          setCommandPaletteOpen(false)
        }
        onNewAnalysis={() => {
          setCommandPaletteOpen(false);
          onNewAnalysis();
        }}
      />
    </div>
  );
};

export default AppShell;