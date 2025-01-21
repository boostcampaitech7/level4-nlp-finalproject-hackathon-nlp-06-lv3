import { useEffect, useState } from "react"
import GoogleLoginBtn from "@/containers/auth/GoogleLogin.tsx"
import axiosInstance from "@/utils/axiosInstance.ts"

function App() {
  const [userId, setUserId] = useState(0)
  const [userProfile, setUserProfile] = useState<any>({})

  useEffect(() => {
    axiosInstance.get("/auth/is-login").then((res) => {
      if (res.data.is_login) setUserId(res.data.user_id)
    })
  }, [])

  useEffect(() => {
    if (userId === 0) return
    axiosInstance.get("/auth/google/profile").then((res) => {
      setUserProfile(res.data)
    })
  }, [userId, setUserProfile])

  return (
    <div className="flex flex-col w-full px-5 py-10 items-center">
      {userId !== 0 ? (
        <div>
          <p>userId: {userId}</p>
          <div>
            <p>{userProfile.name}</p>
            <p>{userProfile.email}</p>
            <img src={userProfile.picture} alt="profile" />
            <p>{userProfile.toString()}</p>
            <button
              type="button"
              onClick={() => {
                axiosInstance.post("/auth/logout").then(() => {
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
