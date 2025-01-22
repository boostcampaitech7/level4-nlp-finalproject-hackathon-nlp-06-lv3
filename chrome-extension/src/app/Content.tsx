import { useEffect } from "react"
import { useRecoilValue, useSetRecoilState } from "recoil"
import GoogleLoginBtn from "@/containers/auth/GoogleLogin.tsx"
import { isLoginState, userIdState } from "@/states/auth.ts"
import UserInfo from "@/containers/profile/UserInfo.tsx"
import useUserLoginInfoQuery from "@/hooks/useUserLoginInfoQuery.ts"

function Content() {
  const setUserId = useSetRecoilState(userIdState)
  const isLogin = useRecoilValue(isLoginState)
  const { userLoginInfo } = useUserLoginInfoQuery()

  useEffect(() => {
    if (!userLoginInfo.is_login) return
    setUserId(userLoginInfo.user_id)
  }, [userLoginInfo])

  return isLogin ? <UserInfo /> : <GoogleLoginBtn />
}

export default Content
