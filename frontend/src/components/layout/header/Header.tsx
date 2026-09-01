import {
  Plus,
  Search,
  Bell,
  UserCircle,
  Activity,
} from "lucide-react";

import "./header.css";

interface HeaderProps {
  onNewAnalysis?: () => void;
}

const Header = ({ onNewAnalysis }: HeaderProps) => {
  return (
    <header className="atlas-header">
      <div className="atlas-header__inner">

        {/* =====================================================
            LEFT — PROJECT
        ===================================================== */}

        <div className="atlas-header__left">

          <button
            type="button"
            className="atlas-header__project"
          >
            Untitled.atlas
          </button>

          <button
            type="button"
            aria-label="New analysis"
            onClick={onNewAnalysis}
            className="atlas-header__new"
          >
            <Plus size={18} strokeWidth={1.5} />
          </button>

        </div>


        {/* =====================================================
            CENTER — ANALYSIS STATUS
        ===================================================== */}

        <div className="atlas-header__status">

          <div className="atlas-header__status-item">
            <span>IMAGE</span>
            <strong>25089_sat.jpg</strong>
          </div>

          <div className="atlas-header__status-item">
            <span>MODEL</span>
            <strong>ATLAS Ensemble</strong>
          </div>

          <div className="atlas-header__status-item atlas-header__status-item--risk">
            <span>RISK</span>
            <strong>HIGH</strong>
          </div>

          <div className="atlas-header__status-item">
            <span>INFERENCE</span>
            <strong>4312 ms</strong>
          </div>

        </div>


        {/* =====================================================
            RIGHT — SYSTEM
        ===================================================== */}

        <div className="atlas-header__right">

          {/* BACKEND */}

          <div className="atlas-header__backend">

            <Activity
              size={14}
              strokeWidth={1.6}
            />

            <span>Backend</span>

            <i />

            <strong>Online</strong>

          </div>


          {/* SEARCH */}

          <button
            type="button"
            className="atlas-header__search"
          >
            <Search
              size={15}
              strokeWidth={1.6}
            />

            <span>Search</span>

            <kbd>Ctrl K</kbd>

          </button>


          {/* NOTIFICATIONS */}

          <button
            type="button"
            aria-label="Notifications"
            className="atlas-header__icon"
          >
            <Bell
              size={17}
              strokeWidth={1.5}
            />
          </button>


          {/* USER */}

          <button
            type="button"
            className="atlas-header__user"
          >
            <UserCircle
              size={17}
              strokeWidth={1.5}
            />

            <span>Guest</span>

          </button>

        </div>

      </div>
    </header>
  );
};

export default Header;