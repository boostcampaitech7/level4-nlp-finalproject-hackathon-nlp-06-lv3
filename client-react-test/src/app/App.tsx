import { useState } from "react"
import reactLogo from "/svg/react.svg"
import viteLogo from "/svg/vite.svg"
import { GoogleOAuthProvider } from "@react-oauth/google"
import GoogleLoginBtn from "@/app/GoogleLogin.tsx"

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank" rel="noreferrer noopener">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" rel="noreferrer noopener">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button type="button" onClick={() => setCount((_count) => _count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">Click on the Vite and React logos to learn more</p>
      <GoogleOAuthProvider clientId="814835238278-fesn4cl6798n00p2ljbtlnsqbk9bfbj8.apps.googleusercontent.com">
        <GoogleLoginBtn />
      </GoogleOAuthProvider>
    </>
  )
}

export default App
