/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F6F8FC",
        "main-theme": "#2C2C2C",
        "text-gray": "#757575",
        "border-gray": "#D9D9D9",
      },
      dropShadow: {
        main: "0 4px 2px rgba(0, 0, 0, 0.25)",
        small: "0 2px 1px rgba(0, 0, 0, 0.25)",
      },
    },
    fontFamily: {
      GmarketSansMedium: ["GmarketSansMedium", "Arial", "Helvetica", "sans-serif"],
      SUITRegular: ["SUIT-Regular", "Arial", "Helvetica", "sans-serif"],
      Inter: ["Inter", "Arial", "Helvetica", "sans-serif"],
    },
  },
  plugins: [],
}
