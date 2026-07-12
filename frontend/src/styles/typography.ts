// src/styles/typography.ts

export const typography = {
  fontFamily: {
    sans: [
      "Inter",
      "Geist",
      "system-ui",
      "sans-serif",
    ].join(", "),
  },

  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  fontSize: {
    xs: "12px",
    sm: "14px",
    base: "16px",
    lg: "18px",
    xl: "20px",
    "2xl": "24px",
    "3xl": "30px",
    "4xl": "36px",
  },

  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.7,
  },

  letterSpacing: {
    tight: "-0.03em",
    normal: "0em",
    wide: "0.04em",
  },
} as const;

export type Typography = typeof typography;