/** Design tokens: warm white, forest green, soft neutral surfaces. */
module.exports = {
  darkMode: "class", // app is light-only; "media" makes NativeWind web throw in dev
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        canvas: "#FBF8F3",
        surface: "#F2EDE4",
        card: "#FFFFFF",
        line: "#E3DCCF",
        ink: "#1B2A21",
        muted: "#55645A",
        forest: { DEFAULT: "#1F5D3A", dark: "#164A2D", soft: "#E3EFE7" },
        c1: "#1F5D3A", // generally accepted
        c2: "#8A5A00", // concern in context
        c3: "#9B2C2C", // restricted
        c4: "#4A5560", // insufficient evidence
        c5: "#5B3F8C", // context dependent
        c6: "#3D4B57", // unmatched
      },
      borderRadius: { xl2: "20px" },
    },
  },
  plugins: [],
};
