import { useEffect, useState } from "react"
import axios from "axios"
import GoogleLoginBtn from "@/app/GoogleLogin.tsx"

function App() {
  const [userId, setUserId] = useState(0)
  const [userProfile, setUserProfile] = useState({})

  useEffect(() => {
    if (userId !== 0) {
      axios.get("http://localhost:8000/auth/google/profile").then((res) => {
        setUserProfile(res.data)
      })
    }
  }, [userId])

  return (
    <div className="flex flex-col w-full mx-5 my-10 items-center">
      {userId !== 0 ? (
        <div>
          <p>userId: {userId}</p>
          <div>
            <p>{userProfile.toString()}</p>
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
        <GoogleLoginBtn setUserId={setUserId} />
      )}
    </div>
  )
}

export default App
