import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import * as path from "path"
import hotReloadExtension from "hot-reload-extension-vite"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    hotReloadExtension({
      log: true,
      backgroundPath: "src/app/App.tsx", // src/pages/background/index.ts
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
