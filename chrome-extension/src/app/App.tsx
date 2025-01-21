import { useEffect, useState } from "react"
import { useRecoilValue, useSetRecoilState } from "recoil"
import GoogleLoginBtn from "@/containers/auth/GoogleLogin.tsx"
import axiosInstance from "@/utils/axiosInstance.ts"
import { isLoginState, userIdState } from "@/states/auth.ts"

function App() {
  const setUserId = useSetRecoilState(userIdState)
  const isLogin = useRecoilValue(isLoginState)
  const [userProfile, setUserProfile] = useState<any>({})

  useEffect(() => {
    axiosInstance.get("/auth/is-login").then((res) => {
      if (res.data.is_login) setUserId(res.data.user_id)
    })
  }, [])

  useEffect(() => {
    if (!isLogin) return
    axiosInstance.get("/auth/google/profile").then((res) => {
      setUserProfile(res.data)
    })
  }, [isLogin, setUserProfile])

  return (
    <div className="flex flex-col w-full px-5 py-10 items-center">
      {isLogin ? (
        <div>
          <div>
            <p>{userProfile.name}</p>
            <p>{userProfile.email}</p>
            <img src={userProfile.picture} alt="profile" />
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
        <GoogleLoginBtn />
      )}
    </div>
  )
}

export default App
