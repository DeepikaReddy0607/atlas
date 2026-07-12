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
        h-screen
        w-screen
        overflow-hidden
        bg-[var(--atlas-bg)]
        text-[var(--atlas-text)]
      "
      style={{
        gridTemplateRows:
          "var(--header-height) 1fr var(--status-height)",
      }}
    >
      {/* Header */}
      <Header />

      {/* Main Area */}
      <div className="flex overflow-hidden">

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