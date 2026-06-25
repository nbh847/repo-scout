import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18202f",
        muted: "#667085",
        canvas: "#eef2f6",
        surface: "#f8fafc",
        panel: "#f7f9fc",
        line: "#d7dee8",
        accent: "#0f766e",
        "accent-soft": "#dff5ef",
        amber: "#b45309",
      },
      boxShadow: {
        soft: "0 10px 34px rgba(24, 32, 47, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
