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
          yellow: "#FFD000",
          "yellow-hover": "#E6BB00",
          "yellow-light": "#FFF3B0",
          black: "#0A0A0A",
          "black-soft": "#1A1A1A",
          white: "#FFFFFF",
          gray: {
            50: "#FAFAFA",
            100: "#F5F5F5",
            200: "#E5E5E5",
            300: "#D4D4D4",
            400: "#A3A3A3",
            500: "#737373",
            600: "#525252",
            700: "#404040",
            800: "#262626",
            900: "#171717",
          },
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        ifb: "4px",
        "ifb-md": "8px",
        "ifb-lg": "12px",
      },
      maxWidth: {
        ifb: "1440px",
      },
      boxShadow: {
        ifb: "4px 4px 0 0 #FFD000",
        "ifb-black": "4px 4px 0 0 #0A0A0A",
        "ifb-sm": "2px 2px 0 0 #FFD000",
      },
    },
  },
  plugins: [],
};

export default config;
