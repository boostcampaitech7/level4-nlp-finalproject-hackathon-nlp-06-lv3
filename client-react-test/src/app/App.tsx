import { useEffect, useState } from "react"
import { GoogleOAuthProvider } from "@react-oauth/google"
import axios from "axios"
import GoogleLoginBtn from "@/app/GoogleLogin.tsx"

function App() {
  const [userId, setUserId] = useState(0)
  const [userProfile, setUserProfile] = useState({})

  useEffect(() => {
    axios
      .get("http://localhost:8000/auth/google/profile", { withCredentials: true })
      .then((res) => {
        setUserId(res.data.user_id)
        setUserProfile(res.data)
        console.log(res.data)
      })
      .catch(() => {
        setUserId(0)
        setUserProfile({})
      })
    console.log("hello")
  }, [userId, setUserId, setUserProfile])
  return (
    <div className="flex flex-col w-full px-5 py-10 items-center">
      {userId !== 0 ? (
        <div>
          <p>userId: {userId}</p>
          <div>
            <button
              type="button"
              onClick={() => {
                axios.post("http://localhost:8000/auth/logout").then(() => {
                  setUserId(0)
                  setUserProfile({})
                })
              }}
            >
              로그아웃
            </button>
          </div>
        </div>
      ) : (
        <GoogleOAuthProvider clientId="814835238278-fesn4cl6798n00p2ljbtlnsqbk9bfbj8.apps.googleusercontent.com">
          <GoogleLoginBtn setUserId={setUserId} />
        </GoogleOAuthProvider>
      )}
    </div>
  )
}

export default App
