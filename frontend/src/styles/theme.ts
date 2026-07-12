// src/styles/theme.ts

export const theme = {
  colors: {
    background: "#0B1220",
    surface: "#111827",
    elevated: "#172033",

    border: "#263041",

    text: {
      primary: "#F8FAFC",
      secondary: "#CBD5E1",
      muted: "#94A3B8",
    },

    primary: "#3B82F6",

    success: "#22C55E",
    warning: "#F59E0B",
    danger: "#EF4444",
  },

  radius: {
    sm: "6px",
    md: "10px",
    lg: "14px",
    xl: "18px",
  },

  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },

  header: {
    height: 64,
  },

  dock: {
    width: 72,
  },

  inspector: {
    width: 340,
  },

  statusBar: {
    height: 32,
  },

  transition: {
    fast: "150ms ease",
    normal: "200ms ease",
    slow: "300ms ease",
  },
} as const;

export type AtlasTheme = typeof theme;