export const motion = {
  duration: {
    fast: 150,
    normal: 200,
    slow: 300,
  },

  easing: {
    standard: "ease",
    smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
  },
} as const;

export type Motion = typeof motion;