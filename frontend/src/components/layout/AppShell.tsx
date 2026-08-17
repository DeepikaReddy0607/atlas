import Header from "./header/Header";
import Dock from "../dock/Dock";
import Workspace from "../workspace/Workspace";
import Inspector from "../inspector/Inspector";
import StatusBar from "../statusbar/StatusBar";

const AppShell = () => {
  return (
    <div
      className="
        grid
        h-full
        w-full
        min-h-0
        min-w-0
        overflow-hidden
        bg-[var(--atlas-bg)]
        text-[var(--atlas-text)]
      "
      style={{
        gridTemplateRows:
          "var(--header-height) minmax(0, 1fr) var(--status-height)",
      }}
    >
      {/* Header */}
      <Header />

      {/* Main Area */}
      <div className="flex min-h-0 min-w-0 flex-1 overflow-hidden">

        <Dock />

        <Workspace />

        <Inspector />

      </div>

      {/* Bottom Status Bar */}
      <StatusBar />

    </div>
  );
};

export default AppShell;