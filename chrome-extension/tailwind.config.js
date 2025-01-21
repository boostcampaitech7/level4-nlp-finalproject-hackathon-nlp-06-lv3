/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#eeeeee",
        "main-theme": "#4064F6",
        "text-gray": "#8D8E92",
      },
    },
    fontFamily: {
      GmarketSansMedium: ["GmarketSansMedium", "Arial", "Helvetica", "sans-serif"],
      SUITRegular: ["SUIT-Regular", "Arial", "Helvetica", "sans-serif"],
    },
  },
  plugins: [],
}
