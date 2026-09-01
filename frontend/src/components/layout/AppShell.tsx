import Header from "../layout/header/Header";
import Dock from "../dock/Dock";
import Workspace from "../workspace/Workspace";
import StatusBar from "../statusbar/StatusBar";
import Inspector from "../inspector/Inspector";

interface AppShellProps {
  onNewAnalysis: () => void;
}

const AppShell = ({ onNewAnalysis }: AppShellProps) => {
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
      {/* =====================================================
          HEADER
      ===================================================== */}

      <Header
        onNewAnalysis={onNewAnalysis}
      />

      {/* =====================================================
          MAIN APPLICATION
      ===================================================== */}

      <div className="flex min-h-0 flex-1">

        {/* ===================================================
            LEFT NAVIGATION
        =================================================== */}

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

        {/* ===================================================
            WORKSPACE
        =================================================== */}

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
          />
        </section>

        {/* ===================================================
            RIGHT INSPECTOR
        =================================================== */}

        <Inspector />

      </div>

      {/* =====================================================
          STATUS BAR
      ===================================================== */}

      <StatusBar />
    </div>
  );
};

export default AppShell;