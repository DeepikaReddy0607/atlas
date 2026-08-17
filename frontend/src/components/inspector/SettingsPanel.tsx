import { useEffect, useState } from "react";

import {
  Settings,
  Monitor,
  Eye,
  Network,
  ShieldAlert,
  Server,
  RotateCcw,
  Trash2,
  CheckCircle2,
  XCircle,
} from "lucide-react";

import {
  ATLAS_SETTINGS_KEY,
  DEFAULT_ATLAS_SETTINGS,
  loadAtlasSettings,
  saveAtlasSettings,
  type AtlasSettings,
} from "../../hooks/useAtlasSettings";

const SettingsPanel = () => {
  const [settings, setSettings] =
    useState<AtlasSettings>(
      loadAtlasSettings
    );

  const [backendStatus, setBackendStatus] =
    useState<
      "checking" | "connected" | "offline"
    >("checking");

  /*
   * ---------------------------------------------------------
   * Update Setting
   * ---------------------------------------------------------
   */

  const updateSetting = <
    K extends keyof AtlasSettings
  >(
    key: K,
    value: AtlasSettings[K]
  ) => {
    setSettings((previous) => {
      const updated: AtlasSettings = {
        ...previous,
        [key]: value,
      };

      saveAtlasSettings(updated);

      return updated;
    });
  };

  /*
   * ---------------------------------------------------------
   * Listen for external settings changes
   * ---------------------------------------------------------
   *
   * This allows the panel to stay synchronized if another
   * component changes ATLAS settings.
   */

  useEffect(() => {
    const handleSettingsChange = () => {
      setSettings(loadAtlasSettings());
    };

    window.addEventListener(
      "atlas-settings-change",
      handleSettingsChange
    );

    return () => {
      window.removeEventListener(
        "atlas-settings-change",
        handleSettingsChange
      );
    };
  }, []);

  /*
   * ---------------------------------------------------------
   * Backend Health Check
   * ---------------------------------------------------------
   */

  useEffect(() => {
    let cancelled = false;

    const checkBackend = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/health"
        );

        if (cancelled) return;

        if (response.ok) {
          setBackendStatus("connected");
        } else {
          setBackendStatus("offline");
        }
      } catch {
        if (!cancelled) {
          setBackendStatus("offline");
        }
      }
    };

    checkBackend();

    return () => {
      cancelled = true;
    };
  }, []);

  /*
   * ---------------------------------------------------------
   * Reset Viewer
   * ---------------------------------------------------------
   */

  const resetViewer = () => {
    updateSetting(
      "overlayOpacity",
      DEFAULT_ATLAS_SETTINGS.overlayOpacity
    );
  };

  /*
   * ---------------------------------------------------------
   * Reset All Preferences
   * ---------------------------------------------------------
   */

  const resetPreferences = () => {
    saveAtlasSettings(
      DEFAULT_ATLAS_SETTINGS
    );

    setSettings(
      DEFAULT_ATLAS_SETTINGS
    );
  };

  return (
    <div
      className="
        h-full
        min-h-0
        overflow-y-auto
        p-5
      "
    >
      {/* =====================================================
          Header
      ====================================================== */}

      <div className="flex items-center gap-3">
        <div
          className="
            flex
            h-10
            w-10
            items-center
            justify-center
            rounded-lg
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
          "
        >
          <Settings size={20} />
        </div>

        <div>
          <h2 className="text-xl font-semibold">
            Settings
          </h2>

          <p className="text-sm text-[var(--atlas-text-muted)]">
            Configure ATLAS workspace preferences
          </p>
        </div>
      </div>

      {/* =====================================================
          Appearance
      ====================================================== */}

      <SettingsSection
        icon={<Monitor size={17} />}
        title="Appearance"
      >
        <SettingRow
          title="Theme"
          description="ATLAS interface appearance"
        >
          <span
            className="
              rounded-md
              border
              border-[var(--atlas-border)]
              bg-[var(--atlas-surface)]
              px-3
              py-1.5
              text-sm
            "
          >
            Dark
          </span>
        </SettingRow>

        <SettingRow
          title="Interface density"
          description="Control spacing inside panels"
        >
          <select
            value={settings.density}
            onChange={(event) =>
              updateSetting(
                "density",
                event.target.value as
                  | "comfortable"
                  | "compact"
              )
            }
            className="
              rounded-md
              border
              border-[var(--atlas-border)]
              bg-[var(--atlas-surface)]
              px-3
              py-1.5
              text-sm
              outline-none
            "
          >
            <option value="comfortable">
              Comfortable
            </option>

            <option value="compact">
              Compact
            </option>
          </select>
        </SettingRow>
      </SettingsSection>

      {/* =====================================================
          Viewer
      ====================================================== */}

      <SettingsSection
        icon={<Eye size={17} />}
        title="Viewer"
      >
        <div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">
                Default overlay opacity
              </p>

              <p className="mt-0.5 text-xs text-[var(--atlas-text-muted)]">
                Opacity applied to visualization overlays
              </p>
            </div>

            <span className="text-sm font-medium">
              {Math.round(
                settings.overlayOpacity * 100
              )}
              %
            </span>
          </div>

          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={
              settings.overlayOpacity
            }
            onChange={(event) =>
              updateSetting(
                "overlayOpacity",
                Number(
                  event.target.value
                )
              )
            }
            className="mt-3 w-full"
          />
        </div>

        <button
          type="button"
          onClick={resetViewer}
          className="
            flex
            w-full
            items-center
            justify-center
            gap-2
            rounded-lg
            border
            border-[var(--atlas-border)]
            px-4
            py-2.5
            text-sm
            transition
            hover:bg-[var(--atlas-surface)]
          "
        >
          <RotateCcw size={16} />

          Reset Viewer Preferences
        </button>
      </SettingsSection>

      {/* =====================================================
          Analysis
      ====================================================== */}

      <SettingsSection
        icon={<Network size={17} />}
        title="Analysis"
      >
        <ToggleRow
          title="Show segmentation"
          description="Display segmentation overlay after analysis"
          checked={
            settings.showSegmentation
          }
          onChange={(value) =>
            updateSetting(
              "showSegmentation",
              value
            )
          }
        />

        <ToggleRow
          title="Show topology graph"
          description="Display the extracted road network"
          checked={
            settings.showGraph
          }
          onChange={(value) =>
            updateSetting(
              "showGraph",
              value
            )
          }
        />

        <ToggleRow
          title="Show criticality"
          description="Display infrastructure criticality"
          checked={
            settings.showCriticality
          }
          onChange={(value) =>
            updateSetting(
              "showCriticality",
              value
            )
          }
        />
      </SettingsSection>

      {/* =====================================================
          Simulation
      ====================================================== */}

      <SettingsSection
        icon={<ShieldAlert size={17} />}
        title="Simulation"
      >
        <ToggleRow
          title="Show simulation impact"
          description="Display simulated network changes"
          checked={
            settings.showSimulationImpact
          }
          onChange={(value) =>
            updateSetting(
              "showSimulationImpact",
              value
            )
          }
        />

        <SettingRow
          title="Default scenario"
          description="Failure scenario used by simulation"
        >
          <span
            className="
              rounded-md
              border
              border-[var(--atlas-border)]
              bg-[var(--atlas-surface)]
              px-3
              py-1.5
              text-sm
            "
          >
            Node Failure
          </span>
        </SettingRow>
      </SettingsSection>

      {/* =====================================================
          System
      ====================================================== */}

      <SettingsSection
        icon={<Server size={17} />}
        title="System"
      >
        <SettingRow
          title="Backend"
          description="ATLAS API server"
        >
          <span className="text-sm font-medium">
            localhost:8000
          </span>
        </SettingRow>

        <SettingRow
          title="Connection"
          description="Backend availability"
        >
          {backendStatus ===
            "checking" && (
            <span className="text-sm text-yellow-400">
              Checking...
            </span>
          )}

          {backendStatus ===
            "connected" && (
            <span
              className="
                flex
                items-center
                gap-2
                text-sm
                text-green-400
              "
            >
              <CheckCircle2 size={16} />

              Connected
            </span>
          )}

          {backendStatus ===
            "offline" && (
            <span
              className="
                flex
                items-center
                gap-2
                text-sm
                text-red-400
              "
            >
              <XCircle size={16} />

              Offline
            </span>
          )}
        </SettingRow>
      </SettingsSection>

      {/* =====================================================
          Danger Zone
      ====================================================== */}

      <section
        className="
          mt-5
          rounded-xl
          border
          border-red-500/30
          bg-red-500/5
          p-4
        "
      >
        <div className="mb-3 flex items-center gap-2">
          <Trash2
            size={17}
            className="text-red-400"
          />

          <h3 className="font-semibold text-red-400">
            Danger Zone
          </h3>
        </div>

        <p className="mb-4 text-sm text-[var(--atlas-text-muted)]">
          Reset all locally stored ATLAS preferences.
        </p>

        <button
          type="button"
          onClick={resetPreferences}
          className="
            flex
            w-full
            items-center
            justify-center
            gap-2
            rounded-lg
            border
            border-red-500/40
            px-4
            py-2.5
            text-sm
            text-red-400
            transition
            hover:bg-red-500/10
          "
        >
          <Trash2 size={16} />

          Reset Preferences
        </button>
      </section>
    </div>
  );
};

/* =========================================================
   Section
========================================================= */

interface SettingsSectionProps {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}

const SettingsSection = ({
  icon,
  title,
  children,
}: SettingsSectionProps) => {
  return (
    <section
      className="
        mt-5
        rounded-xl
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-bg)]
        p-4
      "
    >
      <div className="mb-4 flex items-center gap-2">
        {icon}

        <h3 className="font-semibold">
          {title}
        </h3>
      </div>

      <div className="space-y-4">
        {children}
      </div>
    </section>
  );
};

/* =========================================================
   Setting Row
========================================================= */

interface SettingRowProps {
  title: string;
  description: string;
  children: React.ReactNode;
}

const SettingRow = ({
  title,
  description,
  children,
}: SettingRowProps) => {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="min-w-0">
        <p className="text-sm font-medium">
          {title}
        </p>

        <p className="mt-0.5 text-xs text-[var(--atlas-text-muted)]">
          {description}
        </p>
      </div>

      <div className="shrink-0">
        {children}
      </div>
    </div>
  );
};

/* =========================================================
   Toggle Row
========================================================= */

interface ToggleRowProps {
  title: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}

const ToggleRow = ({
  title,
  description,
  checked,
  onChange,
}: ToggleRowProps) => {
  return (
    <label
      className="
        flex
        cursor-pointer
        items-center
        justify-between
        gap-4
      "
    >
      <div>
        <p className="text-sm font-medium">
          {title}
        </p>

        <p className="mt-0.5 text-xs text-[var(--atlas-text-muted)]">
          {description}
        </p>
      </div>

      <input
        type="checkbox"
        checked={checked}
        onChange={(event) =>
          onChange(
            event.target.checked
          )
        }
        className="
          h-4
          w-4
          accent-blue-500
        "
      />
    </label>
  );
};

export default SettingsPanel;