import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18202f",
        muted: "#667085",
        panel: "#f7f9fc",
        line: "#d9e2ef",
        accent: "#0f766e",
        amber: "#b45309",
      },
      boxShadow: {
        soft: "0 18px 60px rgba(24, 32, 47, 0.12)",
      },
    },
  },
  plugins: [],
};

export default config;
