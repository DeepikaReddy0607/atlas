import {
  ArrowRight,
  FolderOpen,
  Plus,
  Satellite,
} from "lucide-react";

import AtlasLogo from "../welcome/AtlasLogo";
import "./home-screen.css";

interface HomeScreenProps {
  onNewAnalysis: () => void;
  onWorkspace: () => void;
}

const HomeScreen = ({
  onNewAnalysis,
  onWorkspace,
}: HomeScreenProps) => {
  return (
    <main className="atlas-home">
      {/* Background */}
      <div className="atlas-home__grid" aria-hidden="true" />
      <div className="atlas-home__glow" aria-hidden="true" />

      {/* Header */}
      <header className="atlas-home__header">
        <AtlasLogo size="compact" />

        <div className="atlas-home__status">
          <span className="atlas-home__status-dot" />
          SYSTEM READY
        </div>
      </header>

      {/* Main */}
      <section className="atlas-home__content">
        <div className="atlas-home__intro">
          <p className="atlas-home__eyebrow">
            <Satellite size={15} />
            Infrastructure Intelligence Platform
          </p>

          <h1>
            What do you want
            <br />
            to work on?
          </h1>

          <p className="atlas-home__description">
            Analyze satellite imagery, inspect infrastructure
            networks, and explore resilience insights from a
            unified geospatial workspace.
          </p>
        </div>

        {/* Action cards */}
        <div className="atlas-home__actions">

          {/* New Analysis */}
          <button
            type="button"
            onClick={onNewAnalysis}
            className="atlas-home__card atlas-home__card--primary"
          >
            <div className="atlas-home__card-icon">
              <Plus size={24} strokeWidth={1.8} />
            </div>

            <div className="atlas-home__card-body">
              <span className="atlas-home__card-kicker">
                Start fresh
              </span>

              <h2>New Analysis</h2>

              <p>
                Import satellite imagery and run the
                complete ATLAS intelligence pipeline.
              </p>
            </div>

            <ArrowRight
              className="atlas-home__card-arrow"
              size={20}
            />
          </button>

          {/* Workspace */}
          <button
            type="button"
            onClick={onWorkspace}
            className="atlas-home__card"
          >
            <div className="atlas-home__card-icon">
              <FolderOpen size={23} strokeWidth={1.8} />
            </div>

            <div className="atlas-home__card-body">
              <span className="atlas-home__card-kicker">
                Continue working
              </span>

              <h2>Workspace</h2>

              <p>
                Open the geospatial workstation and inspect
                existing analysis layers and results.
              </p>
            </div>

            <ArrowRight
              className="atlas-home__card-arrow"
              size={20}
            />
          </button>

        </div>

        {/* Footer hint */}
        <p className="atlas-home__hint">
          Select an option to continue
        </p>
      </section>

      <footer className="atlas-home__footer">
        <span>ATLAS</span>
        <span>Infrastructure Intelligence</span>
        <span>v1.0</span>
      </footer>
    </main>
  );
};

export default HomeScreen;