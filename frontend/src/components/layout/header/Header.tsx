import {
  Plus,
  Search,
  Bell,
  UserCircle,
  Activity,
} from "lucide-react";

import "./header.css";
import { useState } from "react";
import { useWorkspace } from "../../../context/WorkspaceContext";

interface HeaderProps {
  onNewAnalysis?: () => void;
  onOpenCommandPalette?: ()  => void;
}

const Header = ({ onNewAnalysis, onOpenCommandPalette, }: HeaderProps) => {
  const {
  activeWorkspace,
  renameWorkspace,
} = useWorkspace();

const [renaming, setRenaming] =
  useState(false);

const [nameDraft, setNameDraft] =
  useState(activeWorkspace.name);
  const startRename = () => {
  setNameDraft(activeWorkspace.name);
  setRenaming(true);
};

const finishRename = () => {
  const name =
    nameDraft.trim();

  if (name) {
    renameWorkspace(
      activeWorkspace.id,
      name
    );
  }

  setRenaming(false);
};
  return (
    <header className="atlas-header">
      <div className="atlas-header__inner">

        {/* =====================================================
            LEFT — PROJECT
        ===================================================== */}

        <div className="atlas-header__left">

          {renaming ? (
            <input
              autoFocus
              value={nameDraft}
              onChange={(event) =>
                setNameDraft(event.target.value)
              }
              onBlur={finishRename}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  finishRename();
                }

                if (event.key === "Escape") {
                  setRenaming(false);
                }
              }}
              className="
                w-[180px]
                border
                border-[#31563b]
                bg-[#07130c]
                px-2
                py-1
                text-sm
                text-[#E8F0E8]
                outline-none
              "
            />
          ) : (
            <button
              type="button"
              className="atlas-header__project"
              onDoubleClick={startRename}
              title="Double-click to rename workspace"
            >
              {activeWorkspace.name}
            </button>
          )}

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
            onClick={onOpenCommandPalette}
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