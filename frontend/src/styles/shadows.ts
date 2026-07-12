export const shadows = {
  none: "none",

  sm: "0 1px 2px rgba(0,0,0,0.18)",

  md: "0 4px 10px rgba(0,0,0,0.22)",

  lg: "0 10px 30px rgba(0,0,0,0.28)",

  xl: "0 18px 40px rgba(0,0,0,0.35)",
} as const;

export type Shadows = typeof shadows;