import { useEffect, useState } from "react";

export const ATLAS_SETTINGS_KEY = "atlas-settings";

export interface AtlasSettings {
  theme: "dark";
  density: "comfortable" | "compact";

  overlayOpacity: number;

  showSegmentation: boolean;
  showGraph: boolean;
  showCriticality: boolean;
  showSimulationImpact: boolean;

  defaultScenario: "node_failure";
}

export const DEFAULT_ATLAS_SETTINGS: AtlasSettings = {
  theme: "dark",
  density: "comfortable",

  overlayOpacity: 0.65,

  showSegmentation: true,
  showGraph: true,
  showCriticality: false,
  showSimulationImpact: true,

  defaultScenario: "node_failure",
};

export function loadAtlasSettings(): AtlasSettings {
  try {
    const stored = localStorage.getItem(
      ATLAS_SETTINGS_KEY
    );

    if (!stored) {
      return DEFAULT_ATLAS_SETTINGS;
    }

    const parsed = JSON.parse(stored);

    return {
      ...DEFAULT_ATLAS_SETTINGS,
      ...parsed,
    };
  } catch {
    return DEFAULT_ATLAS_SETTINGS;
  }
}

export function saveAtlasSettings(
  settings: AtlasSettings
) {
  localStorage.setItem(
    ATLAS_SETTINGS_KEY,
    JSON.stringify(settings)
  );

  window.dispatchEvent(
    new Event("atlas-settings-change")
  );
}

export function useAtlasSettings() {
  const [settings, setSettings] =
    useState<AtlasSettings>(
      loadAtlasSettings
    );

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

  return settings;
}