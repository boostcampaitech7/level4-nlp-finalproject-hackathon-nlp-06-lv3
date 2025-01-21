import "@/styles/globals.css"
import React from "react"
import ReactDOM from "react-dom/client"
import { RecoilRoot } from "recoil"
import App from "@/app/App.tsx"

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RecoilRoot>
      <App />
    </RecoilRoot>
  </React.StrictMode>,
)
