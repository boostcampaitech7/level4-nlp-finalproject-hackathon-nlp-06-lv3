import { useEffect, useState } from "react"
import axios from "axios"
import GoogleLoginBtn from "@/app/GoogleLogin.tsx"

function App() {
  const [userId, setUserId] = useState(0)
  const [userProfile, setUserProfile] = useState<any>({})

  useEffect(() => {
    axios.get("http://localhost:8000/auth/is-login", { withCredentials: true }).then((res) => {
      if (res.data.is_login) setUserId(res.data.user_id)
    })
  }, [])

  useEffect(() => {
    if (userId === 0) return
    axios.get("http://localhost:8000/auth/google/profile", { withCredentials: true }).then((res) => {
      setUserProfile(res.data)
      console.log(res.data)
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
        <>
          <GoogleLoginBtn setUserId={setUserId} />
          <button
            type="button"
            onClick={() => {
              axios
                .get("http://localhost:8000/auth/google/profile", { withCredentials: true })
                .then((res) => {
                  setUserProfile(res.data)
                })
                .catch((res) => {
                  console.log("error", res)
                  setUserId(0)
                  setUserProfile({})
                })
            }}
          >
            버튼
          </button>
        </>
      )}
    </div>
  )
}

export default App
