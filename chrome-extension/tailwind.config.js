/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F6F8FC",
        "main-theme": "#4064F6",
        "text-gray": "#757575",
        "border-gray": "#D9D9D9",
      },
    },
    fontFamily: {
      GmarketSansMedium: ["GmarketSansMedium", "Arial", "Helvetica", "sans-serif"],
      SUITRegular: ["SUIT-Regular", "Arial", "Helvetica", "sans-serif"],
    },
  },
  plugins: [],
}
