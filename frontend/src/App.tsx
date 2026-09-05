import { useEffect, useRef, useState } from "react";
import { Toaster } from "sonner";

import AppShell from "./components/layout/AppShell";
import AnalysisPipeline from "./components/analysis/AnalysisPipeline";
import NewAnalysisScreen from "./components/import/NewAnalysisScreen";
import WelcomeScreen from "./components/welcome/WelcomeScreen";
import HomeScreen from "./components/home/HomeScreen";

import { useAtlasAnalysis } from "./hooks/useAtlasAnalysis";

type AppMode =
  | "welcome"
  | "home"
  | "new-analysis"
  | "analysis"
  | "workspace";

const TRANSITION_DURATION = 360;

function App() {
  const [appMode, setAppMode] =
    useState<AppMode>("welcome");

  const [isTransitioning, setIsTransitioning] =
    useState(false);

  const transitionRef =
    useRef<number | null>(null);

  const {
    analyze,
    analysisResult,
    error,
    loading,
    selectedFile,
  } = useAtlasAnalysis();

  /* ==========================================================
     Cleanup transition
  ========================================================== */

  useEffect(() => {
    return () => {
      if (transitionRef.current !== null) {
        window.clearTimeout(
          transitionRef.current
        );
      }
    };
  }, []);

  /* ==========================================================
     Screen transition
  ========================================================== */

  const transitionTo = (mode: AppMode) => {
    setIsTransitioning(true);

    transitionRef.current =
      window.setTimeout(() => {
        setAppMode(mode);
        setIsTransitioning(false);
        transitionRef.current = null;
      }, TRANSITION_DURATION);
  };

  return (
    <>
      <div
        className={
          isTransitioning
            ? "atlas-app-transition"
            : undefined
        }
      >

        {/* ====================================================
            WELCOME
        ==================================================== */}

        {appMode === "welcome" && (
          <WelcomeScreen
            onEnterWorkspace={() =>
              transitionTo("home")
            }
          />
        )}

        {/* ====================================================
            ATLAS HOME
        ==================================================== */}

        {appMode === "home" && (
          <HomeScreen
            onNewAnalysis={() =>
              transitionTo("new-analysis")
            }
            onWorkspace={() =>
              transitionTo("workspace")
            }
          />
        )}

        {/* ====================================================
            NEW ANALYSIS
        ==================================================== */}

        {appMode === "new-analysis" && (
          <NewAnalysisScreen
            onBack={() =>
              transitionTo("home")
            }
            onStartAnalysis={() =>
              setAppMode("analysis")
            }
          />
        )}

        {/* ====================================================
            ANALYSIS PIPELINE
        ==================================================== */}

        {appMode === "analysis" && (
          <AnalysisPipeline
            loading={loading}
            error={error}
            complete={Boolean(analysisResult)}
            onComplete={() =>
              transitionTo("workspace")
            }
            onRetry={() => {
              if (selectedFile) {
                void analyze(selectedFile);
              }
            }}
          />
        )}

        {/* ====================================================
            WORKSPACE
        ==================================================== */}

        {appMode === "workspace" && (
          <AppShell
            onNewAnalysis={() =>
              transitionTo("new-analysis")
            }
          />
        )}

      </div>

      <Toaster
        richColors
        position="bottom-right"
        expand={false}
      />
    </>
  );
}

export default App;