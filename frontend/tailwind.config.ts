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
          black: "#0A0A0A",
          yellow: {
            DEFAULT: "#FFC400",
            light: "#FFD84D",
          },
          white: "#FFFFFF",
          gray: {
            light: "#F5F5F5",
            medium: "#D9D9D9",
          },
          green: "#168A3A",
          red: "#D93025",
          orange: "#E67E00",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
