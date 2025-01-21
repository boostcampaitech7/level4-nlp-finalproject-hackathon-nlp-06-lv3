import { useEffect } from "react"
import { useRecoilValue, useSetRecoilState } from "recoil"
import GoogleLoginBtn from "@/containers/auth/GoogleLogin.tsx"
import axiosInstance from "@/utils/axiosInstance.ts"
import { isLoginState, userIdState } from "@/states/auth.ts"
import UserInfo from "@/containers/profile/UserInfo.tsx"

function App() {
  const isLogin = useRecoilValue(isLoginState)
  const setUserId = useSetRecoilState(userIdState)

  useEffect(() => {
    axiosInstance.get("/auth/is-login").then((res) => {
      if (res.data.is_login) setUserId(res.data.user_id)
    })
  }, [])

  return (
    <div className="flex flex-col w-full px-5 py-10 items-center">{isLogin ? <UserInfo /> : <GoogleLoginBtn />}</div>
  )
}

export default App
