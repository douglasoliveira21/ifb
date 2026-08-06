import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ifb: {
          yellow: "#F4B400",
          "yellow-hover": "#D9A000",
          "yellow-light": "#FFF8E1",
          black: "#111111",
          white: "#FFFFFF",
          bg: "#FFFFFF",
          "gray-50": "#F6F7F9",
          "gray-100": "#E9ECEF",
          "gray-200": "#E5E7EB",
          "gray-300": "#D1D5DB",
          "gray-400": "#9CA3AF",
          "gray-500": "#6B7280",
          "gray-700": "#374151",
          "gray-900": "#1A1A1A",
          green: "#16A34A",
          red: "#DC2626",
          blue: "#2563EB",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        "ifb": "16px",
        "ifb-lg": "20px",
        "ifb-btn": "14px",
      },
      maxWidth: {
        "ifb": "1440px",
      },
      boxShadow: {
        "ifb": "0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.03)",
        "ifb-md": "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.03)",
        "ifb-lg": "0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.03)",
      },
    },
  },
  plugins: [],
};

export default config;
