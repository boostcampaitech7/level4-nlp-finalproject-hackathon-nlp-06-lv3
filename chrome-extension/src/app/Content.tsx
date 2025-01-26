import { useEffect } from "react"
import { useRecoilValue, useSetRecoilState } from "recoil"
import GoogleLoginBtn from "@/containers/auth/GoogleLogin"
import { isLoginState, userIdState } from "@/states/auth"
import UserInfo from "@/containers/profile/UserInfo"
import useUserLoginInfoQuery from "@/hooks/useUserLoginInfoQuery"

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
