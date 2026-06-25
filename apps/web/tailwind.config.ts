import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#d9f4ee",
        muted: "#78909c",
        canvas: "#05080d",
        surface: "#071018",
        panel: "#0b151f",
        line: "#1f3342",
        accent: "#45f58d",
        "accent-soft": "#0f2f20",
        cyan: "#27d8ff",
        amber: "#f5b74d",
      },
      boxShadow: {
        terminal: "0 18px 60px rgba(0, 0, 0, 0.28)",
        radar: "0 0 28px rgba(69, 245, 141, 0.16)",
      },
      backgroundImage: {
        grid:
          "linear-gradient(rgba(69, 245, 141, 0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(39, 216, 255, 0.035) 1px, transparent 1px)",
        scanline: "linear-gradient(rgba(255, 255, 255, 0.035) 50%, transparent 50%)",
        signal: "linear-gradient(90deg, #45f58d, #27d8ff)",
      },
      backgroundSize: {
        grid: "32px 32px",
        scanline: "100% 4px",
      },
    },
  },
  plugins: [],
};

export default config;
