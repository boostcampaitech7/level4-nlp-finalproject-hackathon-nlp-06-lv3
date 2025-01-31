/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F6F8FC",
        "main-theme": "#4064F6",
        "text-gray": "#4b4b4b",
      },
    },
    fontFamily: {
      GmarketSansMedium: ["GmarketSansMedium", "Arial", "Helvetica", "sans-serif"],
      SUITRegular: ["SUIT-Regular", "Arial", "Helvetica", "sans-serif"],
    },
  },
  plugins: [],
}
